import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment variables for secure credentials
load_dotenv()

# Configuration variables (Make sure these match your .env or replace the fallbacks)
QDRANT_URL = os.getenv("QDRANT_URL", "k-proj-3VfprwodkPJ1-zCghFIPxg8NBvI3BCKfdJyClrLtz1-262qBOQoY4_fF8OLOuk7n_1uNmw2Oj7T3BlbkFJvk7EQBPvzSxffqVsxgd5rVgloG9WTS9dp-qrS-hxBr_7ZXHG5w7FCGSOi2CcASVrRc5BuZvTQA")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MGE1ZTVlYTUtYWE5My00NWExLTliOGItZTI3YTMxMmE0ZDljIn0.dNGtjMQmMjaZixO7xnpSdZykjbs15dK-fybPvlz4eco")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "college_notes") 

def clear_vector_db():
    print("Connecting to Qdrant Cloud...")
    
    try:
        # Initialize the Qdrant Client
        client = QdrantClient(
            url=QDRANT_URL, 
            api_key=QDRANT_API_KEY
        )
        
        # Check if the collection exists before attempting to delete
        if client.collection_exists(collection_name=COLLECTION_NAME):
            client.delete_collection(collection_name=COLLECTION_NAME)
            print(f"✅ Successfully deleted collection: '{COLLECTION_NAME}'")
            print("The vector store is now completely erased and ready for fresh ingestion.")
        else:
            print(f"⚠️ Collection '{COLLECTION_NAME}' does not exist. Nothing to clear.")
            
    except Exception as e:
        print(f"❌ Error clearing the database: {e}")

if __name__ == "__main__":
    clear_vector_db()