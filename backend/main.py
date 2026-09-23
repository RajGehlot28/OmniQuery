import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from embedding_manager import EmbeddingManager
from vector_store import VectorStore
from llm import LLM
from query import answer_query
from db_connectors import get_database_schema

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database configuration
# Supported types: "postgresql", "mysql", "mongodb"
DB_TYPE = os.getenv("DB_TYPE", "postgresql")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Load and cache schema if database URL is configured
db_schema = ""
if DATABASE_URL:
    try:
        db_schema = get_database_schema(DB_TYPE, DATABASE_URL)
        print(f"[OmniQuery] Loaded schema for {DB_TYPE.upper()}")
    except Exception as e:
        print(f"[OmniQuery] Warning: Could not connect to {DB_TYPE} at {DATABASE_URL}: {e}")

embedding_manager = EmbeddingManager()
vector_store = VectorStore()
llm_manager = LLM()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: QueryRequest):
    answer, source = await answer_query(
        request.query, 
        vector_store, 
        embedding_manager, 
        llm_manager,
        db_type=DB_TYPE,
        db_url=DATABASE_URL,
        db_schema=db_schema
    )
    return {
        "answer": answer,
        "source": source
    }

@app.get("/db-status")
async def db_status():
    return {
        "db_type": DB_TYPE,
        "is_configured": bool(DATABASE_URL),
        "schema_loaded": bool(db_schema)
    }

