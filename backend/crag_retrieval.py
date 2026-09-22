from reranker import Reranker
from web_search import search_web
from knowledge_refiner import refine_web_results

class CRAGRetrieval:
    def __init__(self, vector_store, embedding_manager, llm_manager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
        self.llm_manager = llm_manager
        self.reranker = Reranker()

    async def retrieve(self, query, top_k=5, score_threshold=0.1):
        # step-1: generate embedding for query and search vector store
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]
        results = await self.vector_store.search(query_embedding, top_k)

        # step-2: filter results based on score threshold
        filtered_results = []
        for point in results.points:
            if point.score >= score_threshold:
                filtered_results.append(point)

        # step-3: if no documents found locally, search on web
        if len(filtered_results) == 0:
            web_data = search_web(query)
            if len(web_data) > 0:
                refined_context = await refine_web_results(query, web_data, self.llm_manager)
                return refined_context, "web_search"
            return "", "none"

        # step-4: rerank the documents and get scores
        scored_results = self.reranker.rerank(query, filtered_results)
        top_score = scored_results[0][0]

        retrieved_docs = []
        for score, point in scored_results:
            retrieved_docs.append(point.payload["text"])


        # step-5: evaluate relevance based on top reranker score - 

        # Case 1: documents are highly relevant (score >= 5.0)
        if top_score >= 5.0:
            return "\n\n".join(retrieved_docs), "vector_db"

        # Case 2: documents are partially relevant (score between 0.0 and 5.0) -> combine with web
        elif top_score >= 0.0:
            local_context = "\n\n".join(retrieved_docs)
            web_data = search_web(query)
            if len(web_data) > 0:
                refined_web = await refine_web_results(query, web_data, self.llm_manager)
                return local_context + "\n\n" + refined_web, "combined"

            return local_context, "vector_db"

        # Case 3: documents are irrelevant -> use web search only
        else:
            web_data = search_web(query)
            if len(web_data) > 0:
                refined_context = await refine_web_results(query, web_data, self.llm_manager)
                return refined_context, "web_search"

            return "", "none"
