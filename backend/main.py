from fastapi import FastAPI
from pydantic import BaseModel
from embedding_manager import EmbeddingManager
from vector_store import VectorStore
from llm import LLM
from query import answer_query

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# loading modules/packages when needed
embedding_manager = None
vector_store = None
llm_manager = None
def get_services():
    global embedding_manager
    global vector_store
    global llm_manager

    if embedding_manager is None:
        embedding_manager = EmbeddingManager()

    if vector_store is None:
        vector_store = VectorStore()

    if llm_manager is None:
        llm_manager = LLM()

    return embedding_manager, vector_store, llm_manager


# creating Pydantic model to get data from request body
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask(request: QueryRequest):
    embedding_manager, vector_store, llm_manager = get_services()
    answer = answer_query(request.query, vector_store, embedding_manager, llm_manager)
    return {"answer" : answer}
