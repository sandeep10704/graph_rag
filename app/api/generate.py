from fastapi import APIRouter
from app.services.mcq_pipeline import generate_mcqs

router = APIRouter()

@router.get("/generate/{graph_id}/{count}")
def generate(graph_id: str, count: int = 10):
    print("GENERATE graph_id:", graph_id)
    return {
        "mcqs": generate_mcqs( graph_id,count)
    }
