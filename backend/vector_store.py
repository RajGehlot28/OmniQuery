import uuid
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (VectorParams, Distance, PointStruct)

class VectorStore:
    def __init__(self, collection_name="college_notes", vector_size=384):
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(
            url = QDRANT_URL,
            api_key = QDRANT_API_KEY
        )


        async def is_collection_exists(self):
            # We use 'await' here because the method is asynchronous
            collections_response = await self.client.get_collections()
            collections = collections_response.collections
            
            if self.collection_name not in [coll.name for coll in collections]:
                await self.client.create_collection(
                    collection_name = self.collection_name,
                    vectors_config = VectorParams(
                        size = self.vector_size,
                        distance = Distance.COSINE
                    )
                )

    async def add_documents(self, chunks, embeddings):
        await self.is_collection_exists()
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
        await self.client.upsert(
            collection_name=self.collection_name,
            points = points
        )

    async def search(self, query_embedding, top_k=5):
        results = await self.client.query_points(
            collection_name = self.collection_name,
            query = query_embedding.tolist(),
            limit = top_k
        )
        return results