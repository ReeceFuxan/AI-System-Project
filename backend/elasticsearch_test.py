from elasticsearch import Elasticsearch

# Connect to Elasticsearch (explicitly specify the scheme)
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Define a sample paper document
paper = {
    "title": "Sample Paper on AI and ML",
    "abstract": "This paper explores the applications of AI in modern technology.",
    "author": "John Doe",
    "published_date": "2025-01-01",
    "content": "Full text of the paper discussing AI algorithms, machine learning models, and their impact."
}

# Attempt to index the document
try:
    response = es.index(index="papers", document=paper)
    print("Document indexed:", response['_id'])
except Exception as e:
    print(f"Error indexing document: {e}")
