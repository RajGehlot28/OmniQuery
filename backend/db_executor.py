import json
from datetime import datetime, date
from decimal import Decimal
from urllib.parse import urlparse
from bson import ObjectId
import pymongo
from sqlalchemy import create_engine, text
from db_connectors import normalize_sql_url

def serialize_row_value(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, ObjectId):
        return str(val)
    return val

def serialize_data(data):
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    if isinstance(data, dict):
        return {k: serialize_data(serialize_row_value(v)) for k, v in data.items()}
    return serialize_row_value(data)

def validate_sql_read_query(query: str):
    cleaned = query.strip()
    if not cleaned:
        return False, "Query is empty."

    # check multiple statements
    if ";" in cleaned.rstrip(";"):
        return False, "Multiple SQL statements are not permitted."

    lower_query = cleaned.lower()
    if not (lower_query.startswith("select") or lower_query.startswith("with")):
        return False, "Only SELECT queries are permitted."

    # check write keywords
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"]
    words = lower_query.split()
    for word in forbidden:
        if word in words:
            return False, f"Write operation '{word}' is not permitted. Only read queries are allowed."

    return True, ""

def _execute_sql_query(db_url: str, db_type: str, query: str, max_rows: int = 50):
    is_safe, reason = validate_sql_read_query(query)
    if not is_safe:
        return {
            "query": query,
            "status": "blocked",
            "message": reason
        }

    normalized_url = normalize_sql_url(db_url, db_type)
    engine = create_engine(normalized_url, pool_pre_ping=True)

    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            keys = list(result.keys()) if result.returns_rows else []
            rows = []
            if result.returns_rows:
                raw_rows = result.fetchmany(max_rows)
                for row in raw_rows:
                    rows.append({k: serialize_row_value(v) for k, v in zip(keys, row)})
            return {
                "query": query,
                "status": "success",
                "row_count": len(rows),
                "data": rows
            }
    except Exception as e:
        return {
            "query": query,
            "status": "error",
            "message": f"{db_type.upper()} execution error: {str(e)}"
        }
    finally:
        engine.dispose()

def execute_postgres_query(db_url: str, query: str, max_rows: int = 50):
    return _execute_sql_query(db_url, "postgresql", query, max_rows)

def execute_mysql_query(db_url: str, query: str, max_rows: int = 50):
    return _execute_sql_query(db_url, "mysql", query, max_rows)

def execute_mongo_query(db_url: str, query, max_docs: int = 50):
    query_dict = query
    if isinstance(query, str):
        try:
            query_dict = json.loads(query)
        except Exception:
            return {
                "query": query,
                "status": "blocked",
                "message": "Invalid JSON format for MongoDB query."
            }

    if not isinstance(query_dict, dict):
        return {
            "query": query,
            "status": "blocked",
            "message": "Query must be a dictionary or JSON object."
        }

    collection_name = query_dict.get("collection")
    operation = query_dict.get("operation", "find").lower()

    allowed_ops = {"find", "aggregate", "count_documents", "distinct"}
    if operation not in allowed_ops:
        return {
            "query": query,
            "status": "blocked",
            "message": f"Operation '{operation}' is not allowed. Only read operations ({', '.join(allowed_ops)}) are permitted."
        }

    # block pipeline write stages
    if operation == "aggregate":
        pipeline = query_dict.get("pipeline", [])
        for stage in pipeline:
            if isinstance(stage, dict):
                for stage_key in stage.keys():
                    if stage_key.lower() in ("$out", "$merge"):
                        return {
                            "query": query,
                            "status": "blocked",
                            "message": f"Stage '{stage_key}' writes data and is not allowed."
                        }

    client = pymongo.MongoClient(db_url, serverSelectionTimeoutMS=5000)
    try:
        parsed = urlparse(db_url)
        db_name = query_dict.get("database") or parsed.path.lstrip("/")
        if not db_name:
            db_names = [d for d in client.list_database_names() if d not in ("admin", "local", "config")]
            db_name = db_names[0] if db_names else "admin"

        db = client[db_name]
        if collection_name not in db.list_collection_names():
            return {
                "query": query,
                "status": "error",
                "message": f"Collection '{collection_name}' not found in '{db_name}'."
            }

        collection = db[collection_name]
        results = []

        if operation == "find":
            limit = min(query_dict.get("limit", max_docs), max_docs)
            cursor = collection.find(query_dict.get("filter", {}), query_dict.get("projection")).limit(limit)
            results = serialize_data(list(cursor))

        elif operation == "aggregate":
            pipeline = query_dict.get("pipeline", [])
            if not any("$limit" in stage for stage in pipeline if isinstance(stage, dict)):
                pipeline.append({"$limit": max_docs})
            cursor = collection.aggregate(pipeline)
            results = serialize_data(list(cursor))

        elif operation == "count_documents":
            count = collection.count_documents(query_dict.get("filter", {}))
            results = [{"count": count}]

        elif operation == "distinct":
            field = query_dict.get("field")
            if not field:
                return {"query": query, "status": "error", "message": "Field required for distinct."}
            distinct_values = collection.distinct(field, query_dict.get("filter", {}))
            results = serialize_data(distinct_values[:max_docs])

        return {
            "query": query,
            "status": "success",
            "count": len(results),
            "data": results
        }
    except Exception as e:
        return {
            "query": query,
            "status": "error",
            "message": f"MongoDB error: {str(e)}"
        }
    finally:
        client.close()
