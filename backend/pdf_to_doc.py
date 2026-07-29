import os
import fitz
from langchain_core.documents import Document
import time

class PdfToDoc:
    def __init__(self, folder_path="./InputData"):
        self.folder_path = folder_path
        self.documents = []

        start_time = time.perf_counter()

        pdf_count = 0
        for filename in os.listdir(self.folder_path):
            # skipping other files
            if not filename.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(self.folder_path, filename)
            pdf = fitz.open(file_path)

            # one document per page
            for page_num, page in enumerate(pdf):
                self.documents.append(
                    Document(
                        page_content=page.get_text(),
                        metadata={ "source" : filename, "page" : page_num+1}
                    )
                )
            pdf_count += 1

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        num_pages = len(self.documents)
        pages_per_sec = num_pages / execution_time if execution_time > 0 else 0

        print("-" * 30)
        print("📄 PDF PARSING METRICS")
        print(f"Total Pages Parsed : {num_pages}")
        print(f"Execution Time     : {execution_time:.4f} seconds")
        print(f"Throughput         : {pages_per_sec:.2f} pages/second")
        print("-" * 30)
        
        print("total pdf's", pdf_count)
        print("total pages:", len(self.documents))

    def get_documents(self):
        return self.documents
    