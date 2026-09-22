from crag_retrieval import CRAGRetrieval

async def answer_query(query, vector_store, embedding_manager, llm_manager):
    # Retrieval using CRAG
    crag = CRAGRetrieval(vector_store, embedding_manager, llm_manager)
    retrieved_context, source = await crag.retrieve(query)

    prompt = f"""
            - You are a helpful assistant for OmniQuery (CRAG Pipeline).
            - Answer the user's question accurately and concisely using ONLY the provided context. 
            - If the context does not contain enough information to answer, state that you cannot find the answer in the available information. 
            - Do not make assumptions or extrapolate beyond what is stated.
            - Give final clear answer for user query.

            Question:
            {query}
            
            Retrieved Context:
            {retrieved_context}

            FINAL ANSWER:
        """

    answer = await llm_manager.invoke(prompt)
    return answer, source