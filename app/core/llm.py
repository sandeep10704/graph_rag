from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv() 

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",
    temperature=0.3,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=OPENAI_API_KEY
)
