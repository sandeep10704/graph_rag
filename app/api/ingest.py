from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chunking import build_chunks
from app.services.graph_store import store_chunks,generate_graph_id
from fastapi import HTTPException
# app/api/routes/ingest.py

from app.schemas.ingest import IngestRequest
from app.services.ingest_service import resolve_text


router = APIRouter()



class IngestResponse(BaseModel):
    status: str
    chunks: int
    graph_id: str

@router.post("/ingest")
def ingest(req: IngestRequest):
    try:
        # 1. Get text from any source
        text = resolve_text(req.input_type, req.value)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted")

        # 2. Build chunks (same pipeline)
        chunk_objects = build_chunks(text)

        if not chunk_objects:
            raise HTTPException(status_code=400, detail="No chunks created")

        # 3. Create isolated graph
        graph_id = generate_graph_id()

        # 4. Store in Neo4j
        store_chunks(chunk_objects, graph_id)

        return {
            "status": "stored",
            "chunks": len(chunk_objects),
            "graph_id": graph_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
