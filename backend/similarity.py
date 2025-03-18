import gensim
from fastapi import FastAPI, Depends
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec, KeyedVectors
from sklearn.preprocessing import normalize
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Paper
import numpy as np

model = gensim.models.KeyedVectors.load_word2vec_format('./data/GoogleNews-vectors-negative300.bin.gz', binary=True) 

# Retrieve the papers' content from the database
def get_papers_from_db(db: Session):
    papers = db.query(Paper).all()
    texts = [paper.content for paper in papers if paper.content]  # Ensure there's content
    return papers, texts

def tokenize(text):
    return text.lower().split()

tokenized_papers = [tokenize(paper) for paper in papers]

def get_word2vec_embedding(tokens, model):
    embeddings = [model[word] for word in tokens if word in model]
    if embeddings:
        return np.mean(embeddings, axis=0)
    else:
        return np.zeros(model.vector_size)

w2v_embeddings = [get_word2vec_embedding(tokens, w2v_model) for tokens in tokenized_papers]


def get_papers_from_db(db):
    """Retrieve paper contents from the database."""
    papers = db.query(Paper).all()
    texts = [paper.content for paper in papers if paper.content]
    return papers, texts

def compute_tfidf_embeddings(texts):
    """Compute TF-IDF embeddings for the given texts."""
    tfidf_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    tfidf_normalized = normalize(tfidf_matrix, axis=1)
    return tfidf_normalized

def compute_word2vec_embeddings(texts):
    """Compute Word2Vec embeddings for the given texts."""
    tokenized_papers = [text.lower().split() for text in texts]

    w2v_model = Word2Vec(tokenized_papers, vector_size=100, window=5, min_count=1, workers=4)

    def get_w2v_embedding(tokens, model):
        embeddings = [model.wv[word] for word in tokens if word in model.wv]
        return np.mean(embeddings, axis=0) if embeddings else np.zeros(model.vector_size)

    w2v_embeddings = [get_w2v_embedding(tokens, w2v_model) for tokens in tokenized_papers]
    w2v_normalized = normalize(w2v_embeddings, axis=1)
    return w2v_normalized

#similarity calculation
def compute_cosine_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    return cosine_similarity([embedding1], [embedding2])[0][0]

def calculate_similarity_between_papers(tfidf_embeddings, w2v_embeddings):
    """Calculate cosine similarities between papers using both TF-IDF and Word2Vec."""
    similarities = []
    for i in range(len(tfidf_embeddings)):
        for j in range(i + 1, len(tfidf_embeddings)):
            tfidf_sim = compute_cosine_similarity(tfidf_embeddings[i], tfidf_embeddings[j])
            w2v_sim = compute_cosine_similarity(w2v_embeddings[i], w2v_embeddings[j])
            similarities.append({
                "paper1_id": i,
                "paper2_id": j,
                "tfidf_similarity": tfidf_sim,
                "w2v_similarity": w2v_sim
            })
    return similarities

def store_similarity_scores_in_db(similarity_data, db):
    store_similarity_scores(similarity_data, db)