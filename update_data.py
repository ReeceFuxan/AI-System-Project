from db_setup import session, User, Paper, Topic

# Update a user's email
user = session.query(User).filter_by(name="Alice Johnson").first()
if user:
    user.email = "alice.new@example.com"
    session.commit()
    print("✅ User email updated successfully!")

# Update a paper title
paper = session.query(Paper).filter_by(title="AI in Medicine").first()
if paper:
    paper.title = "AI in Medicine"
    session.commit()
    print("✅ Paper title updated successfully!")

# Verify changes
updated_user = session.query(User).filter_by(name="Alice Johnson").first()
updated_paper = session.query(Paper).filter_by(id=paper.id).first()

print(f"👤 Updated User: {updated_user.name}, {updated_user.email}")
print(f"📄 Updated Paper: {updated_paper.title}, Author ID: {updated_paper.author_id}")
