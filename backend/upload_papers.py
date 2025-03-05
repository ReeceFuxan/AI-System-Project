from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import fitz
import os
from backend import database, metadata, models
from backend.metadata import store_paper_metadata, index_paper_in_es
from backend.models import PaperMetadata

router = APIRouter()

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