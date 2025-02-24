from elasticsearch import Elasticsearch

# Connect to Elasticsearch instance
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# Define the index settings and mapping
index_mapping = {
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

# Create the index
es.indices.create(index="papers", body=index_mapping, ignore=400)
