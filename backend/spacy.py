import spacy
from gensim import corpora
from gensim.models import LdaModel

nlp = spacy.load('en_core_web_sm')

def preprocess_text(text):
    # Process the text
    doc = nlp(text)

    # Tokenize, remove stop words, and lemmatize
    processed_text = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct
    ]

    return " ".join(processed_text)

# Sample documents (preprocessed text)
documents = [
    "text of paper 1",
    "text of paper 2",
    "text of paper 3",
]

# Preprocess documents
processed_docs = [preprocess_text(doc).split() for doc in documents]

# Create a dictionary and corpus
dictionary = corpora.Dictionary(processed_docs)
corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

# Train LDA model
lda_model = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)

# Display topics
topics = lda_model.print_topics(num_words=5)
for topic in topics:
    print(topic)
    
doc_topic_distribution = lda_model.get_document_topics(corpus[0])