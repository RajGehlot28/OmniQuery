from rag_retrieval import RAGRetrieval

def answer_query(query, vector_store, embedding_manager, llm_manager):
    # Retrieval Pipeline :-

    # step-1 creating vector embedding for query and retrieving relevant embeddings from vectorDB
    rag_retrieval = RAGRetrieval(vector_store, embedding_manager)
    results = rag_retrieval.retrieve(query)

    # sending (query + retrieved-documents) to LLM and ask to generate output
    context = ""
    if len(results) == 0:
        context = "NO_CONTEXT_FOUND"
    else:
        for result in results:
            context += result.payload["text"] + "\n\n"

    prompt = f"""
            SYSTEM:

            You are a strict, zero-hallucination Context Verification Assistant.
            Your sole purpose is to answer the user's question using ONLY the provided text block under "Retrieved Context". You are completely forbidden from using any external knowledge, internal training data, or assumptions.

            CRITICAL CONSTRAINTS:
            - Ground every single sentence of your answer in the provided context.
            - If the context does not contain direct, explicit information to answer the question, or if the context is "NO_CONTEXT_FOUND", you must immediately stop and output exactly this phrase: "I cannot find the answer to this question in the provided documentation."
            - Never attempt to supplement, guess, or use outside general knowledge to answer a question.
            - Return ONLY the final clear answer.
            - Never reveal reasoning, chain of thought, or mention words like "retrieved notes", "embeddings", "context", "database", or "chunks".

            Question:
            {query}
            
            Retrieved Context:
            {context}

            FINAL ANSWER:
        """
    
    answer = llm_manager.invoke(prompt)
    return answer
