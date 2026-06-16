import os
import fitz
from langchain_core.documents import Document

class PdfToDoc:
    def __init__(self, folder_path="./pdfs"):
        self.folder_path = folder_path
        self.documents = []

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

        print("total pdf's", pdf_count)
        print("total pages:", len(self.documents))

    def get_documents(self):
        return self.documents
    