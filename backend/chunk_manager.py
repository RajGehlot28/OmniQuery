from langchain_experimental.text_splitter import SemanticChunker
from sentence_transformer_embeddings import SentenceTransformerEmbeddings

class ChunkManager:
    def __init__(self, documents, embedding_manager):
        self.documents = documents

        embeddings = SentenceTransformerEmbeddings(embedding_manager.model)
        self.text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")

        self.chunks = self.text_splitter.split_documents(documents)
        print("Total semantic chunks:", len(self.chunks))

    def get_chunks(self):
        return self.chunks
