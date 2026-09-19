import asyncio
import os
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient

load_dotenv()

COLLECTION_NAME = "college_notes"

async def clear_db():
    client = AsyncQdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collections = await client.get_collections()
    existing = [c.name for c in collections.collections]

    if COLLECTION_NAME in existing:
        await client.delete_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' deleted successfully.")
    else:
        print(f"Collection '{COLLECTION_NAME}' does not exist. Nothing to clear.")

asyncio.run(clear_db())
