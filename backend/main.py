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

embedding_manager = EmbeddingManager()
vector_store = VectorStore()
llm_manager = LLM()

# creating Pydantic model to get data from request body
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask(request: QueryRequest):
    answer = answer_query(request.query, vector_store, embedding_manager, llm_manager)
    return {"answer" : answer}
    
