from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.models import Base, PaperSimilarity, engine

DATABASE_URL = "postgresql+psycopg2://postgres:csci440@localhost/research_db"  # Ensure this matches your actual PostgreSQL setup

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def store_similarity_scores(similarity_data, db: Session):
    """ Store similarity scores in the database. """
    for data in similarity_data:
        similarity = PaperSimilarity(
            paper1_id=data["paper1_id"],
            paper2_id=data["paper2_id"],
            tfidf_similarity=data["tfidf_similarity"],
            w2v_similarity=data["w2v_similarity"]
        )
        db.add(similarity)
    db.commit()


def store_user_preferences(user_id: int, interests: str, db: Session):
    """ Store or update user research interests. """
    from backend.models import UserProfile

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if user_profile:
        user_profile.interests = interests  # Update existing record
    else:
        new_profile = UserProfile(user_id=user_id, interests=interests)
        db.add(new_profile)

    db.commit()
    return {"message": "User preferences updated successfully"}