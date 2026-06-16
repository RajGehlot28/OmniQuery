from sentence_transformers import SentenceTransformer
class EmbeddingManager:
    # this model has dimension of 384
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def generate_embeddings(self, texts):
        # texts/string converts to embedding, so it takes argument as text/list of texts
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print("embedding shape:", embeddings.shape) # output = (number of chunks, dimension)
        return embeddings
