from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
import json
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError

router = APIRouter()

# Initialize Elasticsearch connection
try:
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Elasticsearch connection failed.")
except ESConnectionError:
    raise HTTPException(status_code=500, detail="Elasticsearch is not running.")

index_name = 'papers'


@router.get("/search_papers")
async def search_papers(request: Request, query: str = Query(..., min_length=2), ignore_unavailable: bool = Query(False)):
    try:
        response = es.search(
            index=index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "author", "content"],
                        "fuzziness": "AUTO",
                        "operator": "AND"
                    }
                }
            },
            ignore_unavailable=ignore_unavailable
        )

        hits = response.get("hits", {}).get("hits", [])

        results = [
            {
                "ID": hit["_id"],
                "Title": hit["_source"].get("title", "No Title"),
                "Author": hit["_source"].get("author", "Unknown Author"),
                "Content": hit["_source"].get("content", "No Content"),
                "Relevance Score": round(hit["_score"], 2),
            }
            for hit in hits
        ]

        formatted_json = json.dumps({"total_results": len(hits), "results": results}, indent=4)

        # You can either log it or return it to the client as a pretty-printed response
        print("Formatted Results:\n", formatted_json)

        return JSONResponse(content=json.loads(formatted_json))

    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Elasticsearch connection error.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")