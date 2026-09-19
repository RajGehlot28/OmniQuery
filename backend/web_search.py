from ddgs import DDGS

def search_web(query, max_results=4):
    results = []
    try:
        with DDGS() as ddgs:
            search_data = ddgs.text(query, max_results=max_results)
            for item in search_data:
                results.append(item["body"])
    except Exception:
        pass
    return results
