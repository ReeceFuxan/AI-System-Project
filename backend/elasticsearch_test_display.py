from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Search for papers with 'AI' in the title
search_query = {
    "query": {
        "match": {
            "title": "AI"
        }
    }
}

# Use 'body' instead of 'query'
response = es.search(index="papers", query=search_query['query'])
print("Search Results:", response)
