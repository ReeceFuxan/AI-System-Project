import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import OperationalError

# Define Base for SQLAlchemy Models
Base = declarative_base()

# Retrieve DATABASE_URL from Railway Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:csci440@localhost:5432/research_db")

# If DATABASE_URL is missing, fall back to local PostgreSQL for testing
if not DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL not found! Using local PostgreSQL.")
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/local_db"

# Debugging: Print the database host (without exposing password)
try:
    print("🔗 Connecting to Database:", DATABASE_URL.split('@')[1])
except IndexError:
    print("⚠️ ERROR: Invalid DATABASE_URL format!")

# Create Database Engine
try:
    engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
    connection = engine.connect()  # Test Connection
    connection.close()
    print("✅ Database Connection Successful!")
except OperationalError as e:
    print("❌ ERROR: Could not connect to the database.")
    print("🔍 Details:", str(e))
    exit(1)  # Stop execution if DB is unreachable

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
