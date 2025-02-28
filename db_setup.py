import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Retrieve the DATABASE_URL from Railway Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:axSSQrThoPOcSoDRtEuVloCdzvdcNdFr@postgres.railway.internal:5432/railway")

# Ensure that the database URL is correctly set
if not DATABASE_URL:
    raise ValueError("ERROR: DATABASE_URL is not set. Please configure it in Railway.")

# Debugging: Print database connection (without password)
print("Connecting to Database:", DATABASE_URL.split('@')[1])

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)

# Define Users Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    papers = relationship("Paper", back_populates="author")

# Define Papers Table
class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    author = relationship("User", back_populates="papers")
    topics = relationship("Topic", back_populates="paper")

# Define Topics Table
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    paper = relationship("Paper", back_populates="topics")

# Create Tables in PostgreSQL
Base.metadata.create_all(engine)

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

