from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.models import Base, engine, PaperSimilarity

Base.metadata.create_all(bind=engine)


DATABASE_URL = "postgresql+psycopg2://postgres:csci440@localhost/research_db"  # Ensure this matches your DB URL

# Setup engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_similarity_scores(similarity_data, db: Session):
    """Store similarity scores in the database."""
    for data in similarity_data:
        similarity = PaperSimilarity(
            paper1_id=data["paper1_id"],
            paper2_id=data["paper2_id"],
            tfidf_similarity=data["tfidf_similarity"],
            w2v_similarity=data["w2v_similarity"]
        )
        db.add(similarity)
    db.commit()