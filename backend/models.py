from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import database

DATABASE_URL = "postgresql+psycopg2://postgres:csci440@localhost/research_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    papers = relationship("Paper", back_populates="author")

class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    abstract = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)

    author_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="papers")
    topics = relationship("Topic", back_populates="paper")

    def __repr__(self):
        return f'<Paper(title={self.title}, author={self.author})>'

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    paper_id = Column(Integer, ForeignKey('papers.id'))
    paper = relationship("Paper", back_populates="topics")

Base.metadata.create_all(bind=engine)