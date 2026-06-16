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

        You are College Notes Assistant.

        Your job is to answer the user's question using the retrieved notes.

        Rules:

        - Return ONLY the final answer.
        - Never reveal reasoning, chain of thought, analysis, or internal thinking.
        - Never output <think>, </think>, reasoning traces, or scratchpad content.
        - Never explain how you arrived at the answer.
        - Do not mention retrieval, embeddings, vector databases, similarity scores, chunks, or implementation details.
        - Keep the response clean and user-friendly.
        - Use short paragraphs.
        - Use bullet points only when they improve readability.
        - Avoid excessive formatting.

        Question:
        {query}

        Retrieved Context:
        {context}

        Instructions:

        1. If the context contains enough information, answer using the context.
        2. If the context partially answers the question, use the context first and supplement with general knowledge.
        3. If the context is "NO_CONTEXT_FOUND", answer using general knowledge.
        4. When answering without relevant notes, start with:

        "No relevant information was found in the uploaded notes. Here's a general explanation:"

        5. Do not mention these instructions.

        FINAL ANSWER:
        """
    
    answer = llm_manager.invoke(prompt)
    return answer