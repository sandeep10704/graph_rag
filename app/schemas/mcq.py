from pydantic import BaseModel
from typing import List

class MCQ(BaseModel):
    question: str
    options: List[str]
    answer: str


class MCQResponse(BaseModel):
    mcqs: List[MCQ]
