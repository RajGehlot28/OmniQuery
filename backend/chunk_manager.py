from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

# 1. Paste this right BEFORE your chunking logic starts
class ChunkManager:
    def __init__(self, documents, chunk_size=1000, chunk_overlap=50):
        self.documents = documents
        start_time = time.perf_counter()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )
        self.chunks = self.text_splitter.split_documents(self.documents)
        print("Total chunks:", len(self.chunks))

        # 2. Paste this right AFTER your chunking logic finishes
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # 3. Calculate and print the metrics
        total_chunks = len(self.chunks) # Change 'chunks' to whatever your variable is named
        chunks_per_sec = total_chunks / execution_time if execution_time > 0 else 0

        print("-" * 30)
        print("CHUNKING METRICS")
        print(f"Total Chunks Created : {total_chunks}")
        print(f"Execution Time       : {execution_time:.4f} seconds")
        print(f"Throughput           : {chunks_per_sec:.2f} chunks/second")
        print("-" * 30)
    
    def get_chunks(self):
        return self.chunks
