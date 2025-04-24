import serpapi
from serpapi import GoogleSearch

def search_scholar(query: str, api_key: str):
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results