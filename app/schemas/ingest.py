from pydantic import BaseModel
from typing import Optional, Literal
# class IngestRequest(BaseModel):
#     text: str


class IngestResponse(BaseModel):
    status: str
    chunks: int
class IngestRequest(BaseModel):
    input_type: Literal["text", "url", "pdf", "topic"]
    value: str