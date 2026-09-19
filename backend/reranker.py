from sentence_transformers import CrossEncoder

class Reranker:
    # cross-encoder model to rerank retrieved chunks based on query relevance
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, results, top_n=3):

        # create (query, chunk_text) pairs for the cross-encoder
        pairs = [(query, result.payload["text"]) for result in results]

        # score each pair — higher score = more relevant
        scores = self.model.predict(pairs)

        # attach scores and sort from highest to lowest
        scored_results = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)

        # return only top_n results after reranking
        return [result for _, result in scored_results[:top_n]]

    def rerank_with_scores(self, query, results, top_n=3):
        # same as rerank but also returns the scores (needed for CRAG grading)
        pairs = [(query, result.payload["text"]) for result in results]
        scores = self.model.predict(pairs)
        scored_results = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
        return scored_results[:top_n]
