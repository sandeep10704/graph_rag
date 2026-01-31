# app/core/tavily.py
import requests

from dotenv import load_dotenv
import os

load_dotenv()  # loads .env into environment variables

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError("TAVILY_API_KEY not found in .env")

def fetch_topic_text(topic: str) -> str:
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": topic,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True,
        "max_results": 5
    }

    res = requests.post(url, json=payload)
    res.raise_for_status()

    data = res.json()

    texts = []
    for r in data.get("results", []):
        if r.get("content"):
            texts.append(r["content"])

    return "\n".join(texts)
