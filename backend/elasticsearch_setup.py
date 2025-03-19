from elasticsearch import Elasticsearch
from typing import List
import json
import os

es = Elasticsearch("http://localhost:9200")

if not es.ping():
    raise ValueError("Elasticsearch connection failed.")
else:
    print("Elasticsearch connection successful.")

INDEX_NAME = "papers"

# Define the index settings and mapping
def create_index():
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(
            index=INDEX_NAME,
            body = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text"},
                        "abstract": {"type": "text"},
                        "author": {"type": "text"},
                        "published_date": {"type": "date"},
                        "content": {"type": "text"},
                        "file_path": {"type": "keyword"},
                        "keywords": {"type": "keyword"},
                    }
                }
            }
        )

def index_paper_in_elasticsearch(paper_id: int, title: str, author: str, abstract: str, content: str, file_path: str, keywords: list = None, published_date: str = None):
    # Create the document to index in Elasticsearch
    document = {
        "title": title,
        "author": author,
        "abstract": abstract,
        "content": content,
        "file_path": file_path,
        "keywords": keywords or [],
        "published_date": published_date
    }

    # Index the document with a unique ID (e.g., using paper_id as the ID)
    response = es.index(index=INDEX_NAME, id=paper_id, document=document)
    return response

create_index()


def load_papers_from_ndjson(file_path: str) -> List[dict]:
    papers = []
    with open('C:/System-Project/kibana.ndjson', 'r') as file:
        for line in file:
            papers.append(json.loads(line))
    return papers

def process_paper_data(papers: List[dict]):
    for paper in papers:
        title = paper.get('title')
        abstract = paper.get('abstract')
        authors = paper.get('authors')

        print(f"Title: {title}")
        print(f"Abstract: {abstract}")
        print(f"Authors: {authors}")
        print("-" * 80)

if __name__ == "__main__":
    file_path = "C:/AI-System-Project/kibana.ndjson"
    papers = load_papers_from_ndjson(file_path)
    process_paper_data(papers)
