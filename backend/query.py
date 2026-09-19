from crag_retrieval import CRAGRetrieval

async def answer_query(query, vector_store, embedding_manager, llm_manager):
    # Retrieval using CRAG
    crag = CRAGRetrieval(vector_store, embedding_manager, llm_manager)
    context, source = await crag.retrieve(query)

    if not context:
        return "I cannot find the answer to this question in the provided documents.", "none"

    prompt = f"""
            SYSTEM:

            You are a strict, zero-hallucination Context Verification Assistant.
            Your purpose is to answer the user's question using ONLY the provided text block under "Retrieved Context". You are completely forbidden from using any external knowledge, internal training data, or assumptions.

            CRITICAL CONSTRAINTS:
            - Ground every single sentence of your answer strictly in the provided context.
            - If the context contains no relevant information at all, or if the context is "NO_CONTEXT_FOUND", output: "I cannot find the answer to this question in the provided documents."
            - If the question contains multiple parts and only some parts are covered in the context, answer the covered parts directly from the context.
            - Never attempt to guess, hallucinate, or use outside general knowledge.
            - Return ONLY the final clear answer.
            - Never reveal reasoning, chain of thought, or mention words like "retrieved notes", "embeddings", "context", "database", or "chunks".

            Question:
            {query}
            
            Retrieved Context:
            {context}

            FINAL ANSWER:
        """

    answer = await llm_manager.invoke(prompt)
    return answer, source