from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Query, Request, Depends
from fastapi.responses import JSONResponse
import json
from sqlalchemy.orm import Session
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from backend import database, metadata, models, elasticsearch_setup
from backend.elasticsearch_setup import es
from backend.models import Paper, PaperMetadata, User, UserProfile
from backend.database import get_db
from backend.metadata import store_paper_metadata, index_paper_in_es
from backend.similarity import compute_tfidf_embeddings, compute_word2vec_embeddings, get_papers_from_db, \
    calculate_similarity_between_papers, store_similarity_scores_in_db
from pydantic import BaseModel
import fitz
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
from sklearn.preprocessing import normalize
import numpy as np

app = FastAPI()
router = APIRouter()


# --- User Profile API Models ---
class UserPreferencesRequest(BaseModel):
    user_id: int
    interests: str  # Comma-separated list of research interests


class UpdateProfileRequest(BaseModel):
    user_id: int
    new_interest: str  # New interest to add


# --- User Profile Endpoints ---
@router.post("/user_preferences")
async def set_user_preferences(preferences: UserPreferencesRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == preferences.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if user_profile:
        user_profile.interests = preferences.interests  # Overwrite existing preferences
    else:
        user_profile = UserProfile(user_id=user.id, interests=preferences.interests)
        db.add(user_profile)

    db.commit()
    return {"message": "User preferences updated successfully"}


@router.post("/update_profile")
async def update_user_profile(update_request: UpdateProfileRequest, db: Session = Depends(get_db)):
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == update_request.user_id).first()

    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Append the new interest if it doesn't already exist
    interests_list = user_profile.interests.split(", ")
    if update_request.new_interest not in interests_list:
        interests_list.append(update_request.new_interest)

    user_profile.interests = ", ".join(interests_list)
    db.commit()

    return {
        "message": "User profile updated successfully",
        "updated_interests": user_profile.interests
    }


# --- Fetch Papers ---
@app.get("/papers/")
def fetch_papers(db: Session = Depends(get_db)):
    papers, texts = get_papers_from_db(db)
    return papers


# --- Search Papers ---
@router.get("/search_papers")
async def search_papers(query: str = Query(..., min_length=2), ignore_unavailable: bool = Query(False)):
    try:
        response = es.search(
            index="papers",
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

        return JSONResponse(content={"total_results": len(hits), "results": results})

    except ESConnectionError:
        raise HTTPException(status_code=500, detail="Elasticsearch connection error.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# --- Personalized Paper Recommendations ---
@router.get("/recommend_papers")
async def recommend_papers(user_id: int, db: Session = Depends(get_db)):
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    interests = user_profile.interests.split(", ")

    # Fetch papers matching user interests
    papers = db.query(Paper).filter(
        Paper.title.ilike(f"%{interests[0]}%") |
        Paper.content.ilike(f"%{interests[0]}%")
    ).all()

    recommendations = [
        {"paper_id": paper.id, "title": paper.title, "author": paper.author.name}
        for paper in papers
    ]

    return {"recommendations": recommendations[:5]}  # Return top 5 results


# --- Upload Paper ---
@router.post("/upload_paper")
async def upload_paper(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        if file.content_type not in ["application/pdf", "text/plain"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and TXT are allowed.")

        file_location = f"temp_files/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        metadata_info = extract_metadata(file_location, file.content_type)
        stored_paper = store_paper_metadata(metadata_info.dict(), file_location, db)

        indexing_result = index_paper_in_es(metadata_info.dict(), stored_paper.id)

        return {
            "filename": file.filename,
            "metadata": metadata_info.dict(),
            "db_status": stored_paper.status,
            "es_status": indexing_result.get("result")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading paper: {str(e)}")


# --- Extract Metadata ---
def extract_metadata(file_path, file_type):
    if file_type == "application/pdf":
        doc = fitz.open(file_path)
        title = doc.metadata.get("title", "Unknown")
        author = doc.metadata.get("author", "Unknown")
        abstract = " ".join([page.get_text() for page in doc])
    elif file_type == "text/plain":
        with open(file_path, "r") as f:
            text = f.read()
        title = text.split("\n")[0]
        author = "Unknown"
        abstract = text[100:500]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    return PaperMetadata(title=title, abstract=abstract, author=author)


# --- Delete Paper ---
@router.delete("/delete_paper/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(database.get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    try:
        es.delete(index="papers", id=paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from Elasticsearch: {str(e)}")

    db.delete(paper)
    db.commit()

    return {"detail": f"Paper {paper_id} deleted successfully"}
