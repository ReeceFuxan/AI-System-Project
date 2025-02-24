from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from backend.models import Paper, User, Topic
from backend.database import get_db  # Assuming you have a get_db function to manage sessions

app = FastAPI()

# Initialize Elasticsearch connection
try:
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Elasticsearch connection failed.")
except ESConnectionError:
    raise HTTPException(status_code=500, detail="Elasticsearch is not running.")

index_name = 'papers'


@app.get("/list_papers")
async def list_papers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        papers = db.query(Paper).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not papers:
        raise HTTPException(status_code=404, detail="No papers found.")

    return {
        "papers": [
            {
                "id": paper.id,
                "title": paper.title,
                "author": paper.author.name,
                "topics": [topic.name for topic in paper.topics]
            }
            for paper in papers
        ]
    }


@app.get("/search_papers")
async def search_papers(query: str = Query(..., min_length=2)):
    try:
        # Perform a search in Elasticsearch
        response = es.search(
            index=index_name,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "author", "abstract"]
                    }
                }
            }
        )

        # Extract search results
        results = [
            {
                "id": hit["_id"],
                "title": hit["_source"]["title"],
                "author": hit["_source"]["author"]
            }
            for hit in response["hits"]["hits"]
        ]

    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Elasticsearch connection error.")

    if not results:
        raise HTTPException(status_code=404, detail="No matching papers found.")

    return {"results": results}
