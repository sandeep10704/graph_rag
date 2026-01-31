# app/services/ingest_service.py
from app.core.loaders import extract_text_from_url, extract_text_from_pdf
from app.core.tavily import fetch_topic_text


def resolve_text(input_type: str, value: str) -> str:
    if input_type == "text":
        return value

    if input_type == "url":
        return extract_text_from_url(value)

    if input_type == "pdf":
        return extract_text_from_pdf(value)

    if input_type == "topic":
        return fetch_topic_text(value)

    raise ValueError("Unsupported input type")
