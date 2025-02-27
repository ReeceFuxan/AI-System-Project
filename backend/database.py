from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, engine

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
