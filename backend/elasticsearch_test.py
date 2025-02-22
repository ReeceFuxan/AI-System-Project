from elasticsearch import Elasticsearch

# Connect using Elasticsearch 7.x client
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Sample paper document
paper = {
    "title": "AI Paper",
    "abstract": "Exploring AI applications.",
    "author": "John Doe",
    "published_date": "2025-01-01",
    "content": "Detailed discussion on AI models."
}

# Index the document
response = es.index(index="papers", document=paper)
print("Document indexed successfully:", response)
