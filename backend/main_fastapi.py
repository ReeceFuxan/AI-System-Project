from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Request, Depends
from fastapi.responses import JSONResponse
import json
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from backend import database, metadata, models, elasticsearch_setup
from backend.models import Paper, PaperMetadata
from backend.database import get_db
from backend.metadata import store_paper_metadata, index_paper_in_es
from pydantic import BaseModel
import fitz
import os

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

@router.post("/upload_paper")
async def upload_paper(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        if file.content_type not in ["application/pdf", "text/plain"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and TXT are allowed.")

        # Save the file temporarily
        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Extract metadata from the uploaded file
        metadata_info = extract_metadata(file_location, file.content_type)

        # Store the paper metadata in the database
        stored_paper = store_paper_metadata(metadata_info.dict(), file_location, db)

        # Index the paper in Elasticsearch
        indexing_result = index_paper_in_es(metadata_info.dict(), stored_paper.id)

        return {
            "filename": file.filename,
            "metadata": metadata_info.dict(),
            "db_status": stored_paper.status,
            "es_status": indexing_result.get("result")  # Fixing incorrect key reference
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading paper: {str(e)}")

def extract_metadata(file_path, file_type):
    if file_type == "application/pdf":
        doc = fitz.open(file_path)
        title = doc.metadata.get("title", "Unknown")
        author = doc.metadata.get("author", "Unknown")
        abstract = " ".join([page.get_text() for page in doc])

        print(f"Extracted Title: {title}")
        print(f"Extracted Author: {author}")
        print(f"Extracted Abstract: {abstract}")

    elif file_type == "text/plain":
        with open(file_path, "r") as f:
            text = f.read()
        title = text.split("\n")[0]  # Assuming title is the first line
        author = "Unknown"
        abstract = text[100:500]  # Example abstract length
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    return PaperMetadata(title=title, abstract=abstract, author=author)

def extract_pdf_metadata(file_path):
    doc = fitz.open(file_path)
    metadata = doc.metadata
    print(f"PDF Metadata: {metadata}")
    return metadata

file_path = 'C:/AI-System-Project/test.pdf'
metadata = extract_pdf_metadata(file_path)

@router.delete("/delete_paper/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(database.get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    es = elasticsearch_setup.es
    try:
        es.delete(index="papers", id=paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from Elasticsearch: {str(e)}")

    db.delete(paper)
    db.commit()

    return {"detail": f"Paper {paper_id} deleted successfully"}