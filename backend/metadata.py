# metadata.py
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
import models
import elasticsearch_setup


# Function to extract metadata
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
        raise ValueError("Unsupported file type.")

    return {"title": title, "author": author, "abstract": abstract}


# Function to store metadata in PostgreSQL
def store_paper_metadata(metadata: dict, file_path: str, db: Session):
    try:
        new_paper = models.Paper(
            title=metadata["title"],
            abstract=metadata["abstract"],
            author=metadata["author"],
            file_path=file_path
        )
        db.add(new_paper)
        db.commit()
        db.refresh(new_paper)
        return new_paper
    except Exception as e:
        db.rollback()
        raise e


# Function to index paper metadata in Elasticsearch
def index_paper_in_es(metadata: dict, paper_id: int):
    es = elasticsearch_setup.es
    es.index(index="papers", id=paper_id, document=metadata)
