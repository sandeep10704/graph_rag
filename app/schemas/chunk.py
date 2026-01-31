from pydantic import BaseModel
from typing import List

class ChunkSchema(BaseModel):
    id: str
    text: str
    keywords: List[str]
