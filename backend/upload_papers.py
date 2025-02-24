from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import fitz
import os
import database
import models
import metadata


app = FastAPI()


class PaperMetadata(BaseModel):
    title: str
    abstract: str
    author: str


@app.post("/upload_paper")
async def upload_paper(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    # Check if file type is allowed
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and TXT are allowed.")

    # Save the file temporarily
    file_location = f"temp_files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())


    metadata_info = metadata.extract_metadata(file_location, file.content_type)

    stored_paper = metadata.store_paper_metadata(metadata_info(), file_location, db)
    paper_id = stored_paper.git("paper_id")

    indexing_result = metadata.index_paper_in_es(metadata_info, paper_id)

    return {
        "filename": file.filename,
        "metadata": metadata_info,
        "db_status": stored_paper.get("status"),
        "es_status": indexing_result.get("status")
    }

def extract_metadata(file_path, file_type):
    if file_type == "application/pdf":
        doc = fitz.open(file_path)
        title = doc.metadata.get("title", "Unknown")
        author = doc.metadata.get("author", "Unknown")
        abstract = " ".join([page.get_text() for page in doc])
    elif file_type == "text/plain":
        with open(file_path, "r") as f:
            text = f.read()
        title = text.split("\n")[0]  # Assuming title is the first line
        author = "Unknown"
        abstract = text[100:500]  # Example abstract length
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    return PaperMetadata(title=title, abstract=abstract, author=author)
