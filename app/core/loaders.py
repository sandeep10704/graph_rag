# app/core/loaders.py
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PyPDF2 import PdfReader


def extract_text_from_url(url: str) -> str:
    res = requests.get(url, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def extract_text_from_pdf(pdf_url: str) -> str:
    res = requests.get(pdf_url, timeout=20)
    res.raise_for_status()

    reader = PdfReader(BytesIO(res.content))
    pages = [p.extract_text() or "" for p in reader.pages]

    return "\n".join(pages)
