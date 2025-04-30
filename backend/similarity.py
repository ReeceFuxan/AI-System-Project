import gensim
from fastapi import FastAPI, Depends, APIRouter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec, KeyedVectors
from sklearn.preprocessing import normalize
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Paper, PaperSimilarity
import numpy as np
import gensim.downloader as api
from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')

app = FastAPI()
router = APIRouter()

model = api.load("glove-wiki-gigaword-100")

def tokenize(text):
    tokens =  [word.lower() for word in word_tokenize(text) if word.isalpha()]
    return tokens

def get_papers_from_db(db: Session):
    papers = db.query(Paper).all()
    return papers, [paper.content for paper in papers if paper.content]

def get_word2vec_embedding(tokens, model):
    embeddings = [model[word] for word in tokens if word in model]
    if embeddings:
        embedding = np.mean(embeddings, axis=0)
        print(f"Generated Word2Vec embedding: {embedding}")
        return embedding
    else:
        print(f"No embeddings found for tokens: {tokens}")
        return np.zeros(model.vector_size)

#similarity calculation
def compute_cosine_similarity(embedding1, embedding2):
    print(f"Embedding 1: {embedding1}")
    print(f"Embedding 2: {embedding2}")
    similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
    print(f"Calculated Cosine Similarity: {similarity}")
    return similarity

@app.get("/papers")
def get_similarities(db: Session = Depends(get_db)):
    papers, texts = get_papers_from_db(db)
    tokenized_papers = [tokenize(paper.content) for paper in papers if paper.content]
    w2v_embeddings = [get_word2vec_embedding(tokens, model) for tokens in tokenized_papers]
    w2v_embeddings = normalize(w2v_embeddings, axis=1)
    tfidf_embeddings = compute_tfidf_embeddings(texts)
    similarities = calculate_similarity_between_papers(tfidf_embeddings, w2v_embeddings, papers)
    store_similarity_scores_in_db(similarities, db)
    return {"similarities": similarities}

def compute_tfidf_embeddings(texts):
    print(f"Raw texts before filtering: {texts}")
    texts = [text for text in texts if text.strip()]
    print(f"Filtered texts: {texts}")
    if not texts:
        raise ValueError("No valid text documents found to process")

    tfidf_vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    tfidf_normalized = normalize(tfidf_matrix, axis=1)
    return tfidf_normalized

def get_weighted_embedding(text, model, vectorizer):
    tokens = tokenize(text)
    # Get the TF-IDF vector for the document.
    tfidf_vector = vectorizer.transform([text])
    feature_names = vectorizer.get_feature_names_out()
    weighted_embeds = []
    weights = []
    for token in tokens:
        if token in model and token in vectorizer.vocabulary_:
            idx = vectorizer.vocabulary_.get(token)
            weight = tfidf_vector[0, idx]
            weighted_embeds.append(model[token] * weight)
            weights.append(weight)
    if weighted_embeds and np.sum(weights) != 0:
        return np.sum(weighted_embeds, axis=0) / np.sum(weights)
    else:
        return np.zeros(model.vector_size)

def calculate_similarity_between_papers(tfidf_embeddings, w2v_embeddings, papers):
    similarities = []  # Initialize an empty list rather than a recursive call
    for i in range(len(tfidf_embeddings)):
        for j in range(i + 1, len(tfidf_embeddings)):
            tfidf_sim = compute_cosine_similarity(tfidf_embeddings[i], tfidf_embeddings[j])
            w2v_sim = compute_cosine_similarity(w2v_embeddings[i], w2v_embeddings[j])
            similarities.append({
                "paper1_id": papers[i].id,
                "paper2_id": papers[j].id,
                "tfidf_similarity": tfidf_sim,
                "w2v_similarity": w2v_sim
            })
    return similarities

def store_similarity_scores_in_db(similarity_data, db: Session):
    for similarity in similarity_data:
        similarity_record = PaperSimilarity(
            paper1_id=similarity['paper1_id'],
            paper2_id=similarity['paper2_id'],
            tfidf_similarity=similarity['tfidf_similarity'],
            w2v_similarity=similarity['w2v_similarity']
        )
        db.add(similarity_record)
    db.commit()

@router.get("/query_similarity")
def compute_similarity_to_query(query: str, db: Session = Depends(get_db)):
    papers, texts = get_papers_from_db(db)
    tokenized_query = tokenize(query)
    query_embedding = get_word2vec_embedding(tokenized_query, model)
    query_embedding = query_embedding.reshape(1, -1)
    print(f"Query Embedding: {query_embedding}")

    results = []
    for paper in papers:
        if not paper.content:
            continue
        tokens = tokenize(paper.content)
        print(f"Tokens for paper '{paper.title}': {tokens}")
        embedding = get_word2vec_embedding(tokens, model)
        print(f"Embedding norm for '{paper.title}': {np.linalg.norm(embedding)}")
        paper_embedding = get_word2vec_embedding(tokens, model).reshape(1, -1)
        print(f"Paper Embedding for {paper.title}: {paper_embedding}")

        if np.all(query_embedding == 0) or np.all(paper_embedding == 0):
            print(f"Zero vector detected for paper {paper.title}")
            continue

        similarity = compute_cosine_similarity(query_embedding, paper_embedding)
        print(f"Similarity for paper {paper.title}: {similarity}")

        results.append({
            "paper_id": paper.id,
            "title": paper.title,
            "author": paper.author,
            "similarity_score": round(float(similarity), 4)
        })

    results = sorted(results, key=lambda x: x["similarity_score"], reverse=True)
    return {"results": results}