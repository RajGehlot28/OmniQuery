from sentence_transformers import CrossEncoder

class Reranker:
    # cross-encoder model to rerank retrieved chunks based on query relevance
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, results):
        # same as rerank but also returns the scores (needed for CRAG grading)
        pairs = [(query, result.payload["text"]) for result in results]
        scores = self.model.predict(pairs)
        scored_results = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
        return scored_results
