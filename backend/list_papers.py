from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from backend.models import Paper
from backend.database import get_db
router = APIRouter()

# Initialize Elasticsearch connection
try:
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Elasticsearch connection failed.")
except ESConnectionError:
    raise HTTPException(status_code=500, detail="Elasticsearch is not running.")

index_name = 'papers'


@router.get("/list_papers")
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
