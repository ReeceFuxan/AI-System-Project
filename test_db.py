from models import SessionLocal, User

session = SessionLocal()

new_user = User(name="Test User", email="test@example.com")
session.add(new_user)
session.commit()

users = session.query(User).all()
for user in users:
    print(user.name, user.email)

session.close()
