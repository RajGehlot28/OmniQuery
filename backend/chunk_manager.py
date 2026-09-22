from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkManager:
    def __init__(self, documents, chunk_size=1000, chunk_overlap=50):
        self.documents = documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        self.chunks = self.text_splitter.split_documents(self.documents)
        total_chunks = len(self.chunks)

        print(f"Total Chunks Created : {total_chunks}")
    
    def get_chunks(self):
        return self.chunks
