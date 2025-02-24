from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models import Paper, User, Topic
from backend.database import get_db  # Assuming you have a get_db function to manage sessions

router = APIRouter()


@router.get("/list_papers")
async def list_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()
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
