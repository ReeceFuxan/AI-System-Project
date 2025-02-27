import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from backend import models
from backend import elasticsearch_setup
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from .models import PaperMetadata


# Function to extract metadata
def extract_metadata(file_path, file_type):
    if file_type == "application/pdf":
        doc = fitz.open(file_path)

        title = doc.metadata.get("title", "Unknown")
        author = doc.metadata.get("author", "Unknown")

        # If title is not found, fall back to the first line of the document text
        if title == "Unknown" or author == "Unknown":
            text = " ".join([page.get_text() for page in doc])
            lines = text.split("\n")
            title = lines[0] if lines else "Untitled"
            author = "Unknown"  # You can add logic here to try and extract the author from the text if needed

        # Extract the abstract (or a portion of the text) as the abstract
        abstract = " ".join([page.get_text() for page in doc])

        return {"title": title, "author": author, "abstract": abstract}

    elif file_type == "text/plain":
        with open(file_path, "r") as f:
            text = f.read()
        title = text.split("\n")[0]  # Assuming title is the first line
        author = "Unknown"
        abstract = text[100:500]  # Example abstract length
    else:
        raise ValueError("Unsupported file type.")

    return PaperMetadata(title=title, abstract=abstract, author=author)


# Function to store metadata in PostgreSQL
def store_paper_metadata(metadata: dict, file_path: str, db: Session):
    if not metadata.get('status'):
        metadata['status'] = 'Pending'

    try:
        author_name = metadata["author"]
        author = db.query(models.User).filter(models.User.name == author_name).first()

        if not author:
            author = models.User(name=author_name, email=f"{author_name.lower().replace(' ', '')}@example.com")
            db.add(author)
            db.commit()
            db.refresh(author)

        new_paper = models.Paper(
            title=metadata["title"],
            abstract=metadata["abstract"],
            file_path=file_path,
            author=author
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
    es = elasticsearch_setup.es  # Use the ES client from your setup file
    try:
        response = es.index(index="papers", id=paper_id, document=metadata)
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to index paper {paper_id} in Elasticsearch: {e}")