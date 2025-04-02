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
import gensim.downloader as api
from gensim.models import Word2Vec

app = FastAPI()

model = api.load("glove-wiki-gigaword-100")

# Retrieve the papers' content from the database
def get_papers_from_db(db: Session):
    papers = db.query(Paper).all()
    texts = [paper.content for paper in papers if paper.content]  # Ensure there's content
    return papers, texts

def tokenize(text):
    return text.lower().split()

def get_word2vec_embedding(tokens, model):
    embeddings = [model[word] for word in tokens if word in model]
    if embeddings:
        return np.mean(embeddings, axis=0)
    else:
        return np.zeros(model.vector_size)

#similarity calculation
def compute_cosine_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

@app.get("/papers")
def get_similarities(db: Session = Depends(get_db)):
    papers, texts = get_papers_from_db(db)

    tokenized_papers = [tokenize(paper) for paper in papers]

    w2v_embeddings = [get_word2vec_embedding(tokens, model) for tokens in tokenized_papers]
    w2v_embeddings = normalize(w2v_embeddings, axis=1)

    tfidf_embeddings = compute_tfidf_embeddings(texts)

    similarities = calculate_similarity_between_papers(tfidf_embeddings, w2v_embeddings)

    store_similarity_scores_in_db(similarities, db)

    return {"similarities": similarities}

def compute_tfidf_embeddings(texts):
    print(f"Raw texts before filtering: {texts}")  # Debugging line
    texts = [text for text in texts if text.strip()]
    print(f"Filtered texts: {texts}")  # Debugging line
    if not texts:
        raise ValueError("No valid text documents found to process")

    texts = [text for text in texts if text.strip()]
    tfidf_vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    tfidf_normalized = normalize(tfidf_matrix, axis=1)
    return tfidf_normalized

def calculate_similarity_between_papers(tfidf_embeddings, w2v_embeddings):
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
    # Implement storing similarity data to the database
    for similarity in similarity_data:
        # Assuming you have a Similarity model, store the scores
        similarity_record = Similarity(
            paper1_id=similarity['paper1_id'],
            paper2_id=similarity['paper2_id'],
            tfidf_similarity=similarity['tfidf_similarity'],
            w2v_similarity=similarity['w2v_similarity']
        )
        db.add(similarity_record)
    db.commit()
