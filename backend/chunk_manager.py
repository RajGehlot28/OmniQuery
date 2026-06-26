from langchain_experimental.text_splitters import SemanticChunker
class ChunkManager:
    def __init__(self, documents, embedding_manager):
        self.documents = documents
        
        # Initializing real semantic splitter using your local model weights
        self.text_splitter = SemanticChunker(
            embedding_manager.model, # passed SentenceTransformer model instance
            breakpoint_threshold_type="percentile" # Splits when similarity drops based no percentile gap
        )
        
        self.chunks = self.text_splitter.split_documents(self.documents)
        print("Total semantic chunks generated:", len(self.chunks))
    
    def get_chunks(self):
        return self.chunks
