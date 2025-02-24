from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import database
import elasticsearch_setup

app = FastAPI()


@app.delete("/delete_paper/{paper_id}")
async def delete_paper(paper_id: int, db: Session = Depends(database.get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    es = elasticsearch_setup.es
    try:
        es.delete(index="papers", id=paper_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting from Elasticsearch: {str(e)}")

    db.delete(paper)
    db.commit()

    return {"detail": f"Paper {paper_id} deleted successfully"}
