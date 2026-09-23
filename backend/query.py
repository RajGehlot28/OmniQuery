import json
from crag_retrieval import CRAGRetrieval
from db_executor import execute_postgres_query, execute_mysql_query, execute_mongo_query

def parse_planner_response(raw_response: str) -> dict:
    # simple clean of markdown fences
    cleaned = raw_response.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {
            "needs_db": False,
            "db_queries": [],
            "blocked_actions": [],
            "needs_crag": True,
            "crag_query": ""
        }

def run_db_queries(db_type: str, db_url: str, queries: list, blocked_actions: list):
    if not db_url or (not queries and not blocked_actions):
        return "", False

    db_type = db_type.lower()
    results = []

    # execute each query one by one
    for q in queries:
        if db_type in ("postgres", "postgresql"):
            res = execute_postgres_query(db_url, q)
        elif db_type == "mysql":
            res = execute_mysql_query(db_url, q)
        elif db_type in ("mongo", "mongodb"):
            res = execute_mongo_query(db_url, q)
        else:
            res = {"query": q, "status": "error", "message": f"Unsupported db: {db_type}"}
        results.append(res)

    lines = []
    for r in results:
        if r.get("status") == "success":
            lines.append(f"Query: {r.get('query')}\nData: {r.get('data')}")
        elif r.get("status") == "blocked":
            lines.append(f"Query Blocked: {r.get('query')}\nReason: {r.get('message')}")
        else:
            lines.append(f"Query Error: {r.get('message')}")

    for action in blocked_actions:
        lines.append(f"Action Blocked: {action}\nReason: Only read operations are supported.")

    return "\n\n".join(lines), True

async def answer_query(
    query: str, 
    vector_store, 
    embedding_manager, 
    llm_manager, 
    db_type: str = "postgresql", 
    db_url: str = "", 
    db_schema: str = ""
):
    has_db = bool(db_url.strip())

    # step-1: ask first llm to plan (decide db and/or crag)
    planner_prompt = f"""
    You are a query planner for OmniQuery.
    Decide if the user question needs database data and/or document/web knowledge.

    Database Type: {db_type if has_db else 'None'}
    Schema:
    {db_schema if (has_db and db_schema) else 'No schema available.'}

    Rules:
    1. If question needs DB, set "needs_db": true and give read-only queries in "db_queries".
    2. Only SELECT queries for SQL. For MongoDB, give query objects. Never generate INSERT, UPDATE, DELETE, or DROP.
    3. If user asked for write/delete, don't generate query, add it to "blocked_actions".
    4. If question needs notes or external info, set "needs_crag": true and provide "crag_query".

    Return ONLY a JSON with this structure:
    {{
      "needs_db": true/false,
      "db_queries": ["query1", "query2"],
      "blocked_actions": ["action description"],
      "needs_crag": true/false,
      "crag_query": "search query"
    }}

    Question: {query}
    """

    plan_raw = await llm_manager.invoke(planner_prompt)
    plan = parse_planner_response(plan_raw)

    needs_db = plan.get("needs_db", False) and has_db
    blocked_actions = plan.get("blocked_actions", [])
    has_db_work = needs_db or bool(blocked_actions and has_db)
    needs_crag = plan.get("needs_crag", False)

    # fallback to crag if nothing chosen
    if not has_db_work and not needs_crag:
        needs_crag = True

    # step-2: execute db queries if needed
    db_context = ""
    has_db_result = False
    if has_db_work:
        db_context, has_db_result = run_db_queries(
            db_type, 
            db_url, 
            plan.get("db_queries", []), 
            blocked_actions
        )

    # step-3: execute crag if needed
    crag_context = ""
    crag_source = "none"
    if needs_crag:
        crag = CRAGRetrieval(vector_store, embedding_manager, llm_manager)
        crag_search_text = plan.get("crag_query") or query
        crag_context, crag_source = await crag.retrieve(crag_search_text)

    # step-4: identify source
    sources = []
    if has_db_result:
        sources.append("database")
    if crag_source and crag_source != "none":
        sources.append(crag_source)
    final_source = " + ".join(sources) if sources else "direct"

    # step-5: build final answer using context
    db_text = f"Database Results:\n{db_context}\n" if db_context else ""
    doc_text = f"Retrieved Notes/Web:\n{crag_context}\n" if crag_context else ""

    prompt = f"""
    - You are a helpful assistant for OmniQuery.
    - Answer the question accurately using ONLY the provided context.
    - If database results are provided, use them.
    - If any write operation was blocked, inform the user that only read operations are supported.
    - If information is not found in context, state that clearly.

    Question: {query}

    {db_text}
    {doc_text}

    FINAL ANSWER:
    """

    answer = await llm_manager.invoke(prompt)
    return answer, final_source