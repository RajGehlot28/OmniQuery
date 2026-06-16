from pdf_to_doc import PdfToDoc
from chunk_manager import ChunkManager
from embedding_manager import EmbeddingManager
from vector_store import VectorStore

def store_vectorDB():
    # Ingestion Pipeline :-

    print("Starting Ingestion...")

    # step-1 converting pdfs to documents
    pdf_to_doc_manager = PdfToDoc()
    documents = pdf_to_doc_manager.get_documents()

    # step-2 splitting documents to chunks
    chunk_manager = ChunkManager(documents, 1000, 50)
    chunks = chunk_manager.get_chunks()

    # step-3 create embeddings for chunks
    embedding_manager = EmbeddingManager()
    texts = [chunk.page_content for chunk in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)

    # step-4 store embeddings into vectorDB (Qdrant DB)
    vector_store = VectorStore()
    vector_store.add_documents(chunks, embeddings)

    print("Ingestion completed")

store_vectorDB()