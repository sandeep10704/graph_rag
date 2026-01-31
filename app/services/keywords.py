import re
from sklearn.feature_extraction.text import TfidfVectorizer

STOPWORDS = {
    "the","is","of","on","and","a","to","has","using","depends"
}

def extract_important_terms(text: str, max_features: int = 10):
    """
    Equivalent to:
    vectorizer = TfidfVectorizer(...)
    IMPORTANT_TERMS = vectorizer.get_feature_names_out()
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=max_features
    )
    vectorizer.fit([text])
    return set(vectorizer.get_feature_names_out())


def extract_keywords(text: str, important_terms: set):
    """
    Same logic as your notebook cell:
    - regex words
    - stopword removal
    - must exist in IMPORTANT_TERMS
    """
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())

    keywords = set()
    for w in words:
        if w not in STOPWORDS and w in important_terms:
            keywords.add(w)

    return list(keywords)
