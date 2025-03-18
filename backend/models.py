from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pydantic import BaseModel

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
    profile = relationship("UserProfile", uselist=False, back_populates="user")  # Link to UserProfile


class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    interests = Column(Text, nullable=True)  # Stores research interests as a comma-separated string

    user = relationship("User", back_populates="profile")


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
    status = Column(String)

    def __repr__(self):
        return f'<Paper(title={self.title}, author={self.author})>'


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    paper_id = Column(Integer, ForeignKey('papers.id'))
    paper = relationship("Paper", back_populates="topics")


class PaperMetadata(BaseModel):
    title: str
    abstract: str
    author: str

    def to_dict(self):
        return {
            "title": self.title,
            "abstract": self.abstract,
            "author": self.author
        }


class PaperSimilarity(Base):
    __tablename__ = 'paper_similarities'
    id = Column(Integer, primary_key=True, index=True)
    paper1_id = Column(Integer, ForeignKey('papers.id'))
    paper2_id = Column(Integer, ForeignKey('papers.id'))
    tfidf_similarity = Column(Integer)
    w2v_similarity = Column(Integer)

    paper1 = relationship("Paper", foreign_keys=[paper1_id])
    paper2 = relationship("Paper", foreign_keys=[paper2_id])


Base.metadata.create_all(bind=engine)
