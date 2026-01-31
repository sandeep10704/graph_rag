import re, uuid
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
# ---------- logger setup ----------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,   # change to INFO in prod
    format="%(asctime)s | %(levelname)s | %(message)s"
)


STOPWORDS = {"the","is","of","and","a","to","in","as"}

def split_structural(text):
    logger.debug("Starting structural split")
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    logger.debug(f"Paragraphs found: {len(paras)}")

    sentences = []
    for p in paras:
        parts = re.split(r'(?<=[.!?])\s+', p)
        sentences.extend(parts)

    logger.debug(f"Total sentences extracted: {len(sentences)}")
    return sentences



def hybrid_chunk(text, window=3, overlap=1):
    logger.debug(f"Hybrid chunking started | window={window}, overlap={overlap}")

    s = split_structural(text)
    step = window - overlap

    chunks = [" ".join(s[i:i+window]) for i in range(0, len(s)-window+1, step)]

    logger.debug(f"Chunks generated before filtering: {len(chunks)}")
    return chunks

def merge_short_chunks(chunks, min_words=40):
    logger.debug(f"Merging short chunks | min_words={min_words}")

    merged = []
    i = 0

    while i < len(chunks):
        words = chunks[i].split()

        if len(words) < min_words and i + 1 < len(chunks):
            combined = chunks[i] + " " + chunks[i + 1]
            merged.append(combined)

            logger.debug(
                f"Merged chunks at index {i} & {i+1} "
                f"(words: {len(words)} + {len(chunks[i+1].split())})"
            )
            i += 2
        else:
            merged.append(chunks[i])
            i += 1

    logger.debug(f"Chunks after merge: {len(merged)}")
    return merged


def extract_important_terms(text):
    logger.debug("Extracting important terms using TF-IDF")

    v = TfidfVectorizer(stop_words="english", max_features=10)
    v.fit([text])

    terms = set(v.get_feature_names_out())
    logger.debug(f"Important terms extracted: {terms}")

    return terms



def extract_keywords(text, important_terms):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    keywords = list({w for w in words if w in important_terms})

    logger.debug(f"Keywords extracted: {keywords}")
    return keywords



def valid_chunk(chunk, important_terms):
    words = re.findall(r"[a-zA-Z]{3,}", chunk.lower())

    if len(words) >= 40:
        logger.debug("Chunk accepted (>=40 words)")
        return True

    hits = sum(w in important_terms for w in words)
    stop_ratio = sum(w in STOPWORDS for w in words) / max(len(words), 1)

    logger.debug(
        f"Chunk stats | words={len(words)} | hits={hits} | stop_ratio={stop_ratio:.2f}"
    )

    valid = hits >= 2 and stop_ratio < 0.4
    logger.debug(f"Chunk valid: {valid}")

    return valid

def build_chunks(full_text):
    logger.debug("Building chunks started")

    important_terms = extract_important_terms(full_text)

    # Step 1: initial chunking
    chunks = hybrid_chunk(full_text)
    logger.debug(f"Chunks before merge: {len(chunks)}")

    # Step 2: merge short chunks
    chunks = merge_short_chunks(chunks)
    logger.debug(f"Chunks after merge: {len(chunks)}")

    # Step 3: validate chunks
    chunks = [c for c in chunks if valid_chunk(c, important_terms)]
    logger.debug(f"Chunks after validation: {len(chunks)}")

    # Step 4: create chunk objects
    chunk_objects = []
    for chunk in chunks:
        cid = f"C_{uuid.uuid4().hex[:8]}"
        keywords = extract_keywords(chunk, important_terms)

        logger.debug(f"Chunk object created | id={cid} | keywords={keywords}")

        chunk_objects.append({
            "id": cid,
            "text": chunk,
            "keywords": keywords
        })

    logger.info(f"Total chunks stored: {len(chunk_objects)}")
    return chunk_objects

