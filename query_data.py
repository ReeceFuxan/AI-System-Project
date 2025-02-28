from db_setup import session, User, Paper, Topic

# Retrieve all users
users = session.query(User).all()
print("\n👤 Users:")
for user in users:
    print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")

# Retrieve all papers with authors
papers = session.query(Paper).all()
print("\n📄 Papers:")
for paper in papers:
    print(f"ID: {paper.id}, Title: {paper.title}, Author ID: {paper.author_id}")

# Retrieve all topics with related papers
topics = session.query(Topic).all()
print("\n📌 Topics:")
for topic in topics:
    print(f"ID: {topic.id}, Name: {topic.name}, Paper ID: {topic.paper_id}")
