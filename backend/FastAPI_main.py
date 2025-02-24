# app.py
from fastapi import FastAPI
from upload_papers import upload_paper  # Import the upload_paper route
from list_papers import list_papers    # Import the list_papers route
from delete_papers import delete_paper  # Import the delete_paper route

app = FastAPI()

# Register the routes
app.include_router(upload_paper)
app.include_router(list_papers)
app.include_router(delete_paper)

