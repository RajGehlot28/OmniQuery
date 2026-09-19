from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

class ChunkManager:
    def __init__(self, documents, chunk_size=1000, chunk_overlap=50):
        self.documents = documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )

        start_time = time.perf_counter() # measuring time
        self.chunks = self.text_splitter.split_documents(self.documents)
        print("Total chunks:", len(self.chunks))

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        total_chunks = len(self.chunks)
        chunks_per_sec = total_chunks / execution_time if execution_time > 0 else 0

        print("-" * 30)
        print("CHUNKING METRICS")
        print(f"Total Chunks Created : {total_chunks}")
        print(f"Execution Time       : {execution_time:.4f} seconds")
        print(f"Throughput           : {chunks_per_sec:.2f} chunks/second")
        print("-" * 30)
    
    def get_chunks(self):
        return self.chunks
