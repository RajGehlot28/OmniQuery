class RAGRetrieval:
    def __init__(self, vector_store, embedding_manager):
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
    
    async def retrieve(self, query, top_k=5, score_threshold=0.1):
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        results = await self.vector_store.search(query_embedding, top_k)

        # considering results/points whose score >= score_threshold
        filtered_results = []
        for result in results.points:
            if result.score >= score_threshold:
                filtered_results.append(result)
        
        return filtered_results

