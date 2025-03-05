# app.py
from fastapi import FastAPI
from backend.upload_papers import router as upload_paper
from backend.list_papers import router as list_papers
from backend.delete_papers import router as delete_paper
from backend.search_papers import router as search_papers

app = FastAPI()

# Register the routes
app.include_router(upload_paper, prefix="/papers")
app.include_router(list_papers, prefix="/papers")
app.include_router(delete_paper, prefix="/papers")
app.include_router(search_papers, prefix="/papers")