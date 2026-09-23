from urllib.parse import urlparse
from sqlalchemy import create_engine, inspect
import pymongo

def normalize_sql_url(db_url: str, db_type: str) -> str:
    db_type_lower = db_type.lower()
    if db_type_lower in ("postgres", "postgresql"):
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
            return db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif db_type_lower == "mysql":
        if db_url.startswith("mysql://") and not db_url.startswith("mysql+"):
            return db_url.replace("mysql://", "mysql+pymysql://", 1)
    return db_url

def get_sql_schema(db_url: str, db_type: str) -> dict:
    normalized_url = normalize_sql_url(db_url, db_type)
    engine = create_engine(normalized_url, pool_pre_ping=True)
    try:
        inspector = inspect(engine)
        schema_dict = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            pk = (inspector.get_pk_constraint(table_name) or {}).get("constrained_columns", [])
            fks = inspector.get_foreign_keys(table_name)
            fk_list = [
                f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                for fk in fks if fk.get("referred_table")
            ]
            schema_dict[table_name] = {
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "is_primary": col["name"] in pk
                    }
                    for col in columns
                ],
                "foreign_keys": fk_list
            }
        return schema_dict
    finally:
        engine.dispose()

def get_postgres_schema(db_url: str) -> dict:
    return get_sql_schema(db_url, "postgresql")

def get_mysql_schema(db_url: str) -> dict:
    return get_sql_schema(db_url, "mysql")

def get_mongo_schema(db_url: str, db_name: str = None) -> dict:
    client = pymongo.MongoClient(db_url, serverSelectionTimeoutMS=5000)
    schema_dict = {}
    try:
        if not db_name:
            parsed = urlparse(db_url)
            path = parsed.path.lstrip("/")
            if path:
                db_name = path
            else:
                db_names = [d for d in client.list_database_names() if d not in ("admin", "local", "config")]
                db_name = db_names[0] if db_names else "admin"

        db = client[db_name]
        for coll_name in db.list_collection_names():
            if coll_name.startswith("system."):
                continue
            collection = db[coll_name]
            sample_docs = list(collection.find().limit(5))
            fields = {}
            for doc in sample_docs:
                for k, v in doc.items():
                    if k not in fields:
                        fields[k] = type(v).__name__
            schema_dict[coll_name] = {
                "fields": fields,
                "sample_count": len(sample_docs)
            }
        return {
            "database_name": db_name,
            "collections": schema_dict
        }
    finally:
        client.close()

def format_schema_for_prompt(schema_info: dict, db_type: str) -> str:
    db_type_lower = db_type.lower()
    lines = []

    if db_type_lower in ("postgres", "postgresql", "mysql"):
        lines.append(f"Database Type: {db_type.upper()}")
        for table, details in schema_info.items():
            col_strs = []
            for col in details.get("columns", []):
                pk_marker = " (PRIMARY KEY)" if col.get("is_primary") else ""
                col_strs.append(f"{col['name']} ({col['type']}{pk_marker})")
            lines.append(f"\nTable: {table}")
            lines.append(f"  Columns: {', '.join(col_strs)}")
            fks = details.get("foreign_keys", [])
            if fks:
                lines.append(f"  Foreign Keys: {'; '.join(fks)}")

    elif db_type_lower in ("mongo", "mongodb"):
        db_name = schema_info.get("database_name", "default")
        collections = schema_info.get("collections", {})
        lines.append(f"Database Type: MongoDB (Database: {db_name})")
        for coll, details in collections.items():
            field_items = [f"{fname} ({ftype})" for fname, ftype in details.get("fields", {}).items()]
            lines.append(f"\nCollection: {coll}")
            lines.append(f"  Fields: {', '.join(field_items) if field_items else 'No documents found'}")

    return "\n".join(lines)

def get_database_schema(db_type: str, db_url: str) -> str:
    db_type_lower = db_type.lower()
    if db_type_lower in ("postgres", "postgresql", "mysql"):
        raw_schema = get_sql_schema(db_url, db_type)
    elif db_type_lower in ("mongo", "mongodb"):
        raw_schema = get_mongo_schema(db_url)
    else:
        raise ValueError(f"Unsupported database type: '{db_type}'")
    return format_schema_for_prompt(raw_schema, db_type)
