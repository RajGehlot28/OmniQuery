from data_to_doc import DataToDoc
from chunk_manager import ChunkManager
from embedding_manager import EmbeddingManager
from vector_store import VectorStore
import asyncio # to call async function

async def store_vectorDB():
    # Ingestion Pipeline :-

    print("Starting Ingestion...")

    # step-1 converting pdfs to documents
    data_to_doc_manager = DataToDoc()
    documents = data_to_doc_manager.get_documents()

    # step-2 splitting documents to chunks
    embedding_manager = EmbeddingManager()
    chunk_manager = ChunkManager(documents, embedding_manager)
    chunks = chunk_manager.get_chunks()

    # step-3 create embeddings for chunks
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)

    # step-4 store embeddings into vectorDB (Qdrant DB)
    vector_store = VectorStore()
    await vector_store.add_documents(chunks, embeddings)

    print("Ingestion completed")


if __name__ == "__main__":
    asyncio.run(store_vectorDB())
