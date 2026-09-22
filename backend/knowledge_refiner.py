async def refine_web_results(query, web_results, llm_manager):
    web_text = "\n\n".join(web_results)

    prompt = f"""
    Given the following question and web search results, extract only the relevant information needed to answer the question.
    Remove any extra or unnecessary details.

    Question: {query}

    Web Results:
    {web_text}

    Relevant Information:
    """

    response = await llm_manager.invoke(prompt)
    return response.strip()
