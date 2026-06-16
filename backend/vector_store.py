import uuid

import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

from qdrant_client import QdrantClient
from qdrant_client.models import (VectorParams, Distance, PointStruct)

class VectorStore:
    def __init__(self, collection_name="college_notes", vector_size=384):
        self.collection_name = collection_name
        self.client = QdrantClient(
            url = QDRANT_URL,
            api_key = QDRANT_API_KEY
        )

        collections = self.client.get_collections().collections
        if collection_name not in [coll.name for coll in collections]:
            self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config = VectorParams(
                    size = vector_size,
                    distance = Distance.COSINE
                )
            )

    def add_documents(self, chunks, embeddings):
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id = str(uuid.uuid4()),
                vector = embedding.tolist(),
                payload = {
                    "text":chunk.page_content,
                    "source":chunk.metadata["source"],
                    "page":chunk.metadata["page"],
                    "chunk_id" : idx
                }
            )
            points.append(point)
        
        # adding points to qdrant-db
        self.client.upsert(
            collection_name=self.collection_name,
            points = points
        )

    def search(self, query_embedding, top_k=5):
        results = self.client.query_points(
            collection_name = self.collection_name,
            query = query_embedding.tolist(),
            limit = top_k
        )
        return results