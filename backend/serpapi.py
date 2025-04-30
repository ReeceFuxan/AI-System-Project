import serpapi
from serpapi import GoogleSearch
import re

def extract_year_from_summary(summary: str) -> str:
    match = re.search(r'\b(19|20)\d{2}\b', summary)
    return match.group(0) if match else "Unknown"

def search_scholar(query: str, api_key: str):
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    print("Full SerpApi response:", results)

    papers = []
    for result in results.get("organic_results", []):
        title = result.get("title", "")
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        pub_info = result.get("publication_info", {})

        # First try to get the year directly
        year = pub_info.get("year")
        if not year:
            summary_text = pub_info.get("summary", "")
            year = extract_year_from_summary(summary_text)

        papers.append({
            "title": title,
            "link": link,
            "snippet": snippet,
            "year": year if year else "Unknown"
        })

    return papers