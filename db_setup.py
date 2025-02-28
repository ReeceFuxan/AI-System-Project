import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Define Base Model for SQLAlchemy
Base = declarative_base()

# Fetch the Render database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is missing, raise an error (this prevents localhost fallback)
if not DATABASE_URL:
    raise ValueError("ERROR: DATABASE_URL is not set. Please configure it in Render.")

# Create the database connection
engine = create_engine(DATABASE_URL)

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
