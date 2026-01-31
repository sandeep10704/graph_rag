from app.core.neo4j import get_driver
driver = get_driver()
from app.core.llm import llm

MAX_TRIES_PER_CHUNK = 3


# ------------------ Difficulty Filter ------------------

def not_easy(question, options):
    print("\n[DEBUG] Checking difficulty filter")
    print("Question:", question)
    print("Options:", options)

    # Relaxed question length
    if len(question.split()) < 8:
        print("[FILTER FAIL] Question too short")
        return False

    # Relaxed option length variance
    lens = [len(o.split()) for o in options]
    if max(lens) - min(lens) > 10:
        print("[FILTER FAIL] Option length variance too high:", lens)
        return False

    banned = ["always", "never", "all", "none"]
    if any(b in question.lower() for b in banned):
        print("[FILTER FAIL] Banned word found")
        return False

    print("[FILTER PASS] Question accepted")
    return True


# ------------------ Neo4j Fetchers ------------------

def fetch_chunks(graph_id):
    print("\n[DEBUG] Fetching chunks from Neo4j")

    query = """
    MATCH (c:Chunk {graph_id: $graph_id})
    RETURN c.id AS id, c.text AS text
    ORDER BY c.id
    """

    with driver.session() as s:
        data = s.run(query, {"graph_id": graph_id}).data()

    print(f"[DEBUG] Total chunks fetched: {len(data)}")
    return data



def get_overlap_texts(chunk_id, graph_id, limit=3):
    print(f"\n[DEBUG] Fetching overlaps for chunk: {chunk_id}")

    query = """
    MATCH (main:Chunk {id: $id, graph_id: $graph_id})
          -[:HAS_KEYWORD {graph_id: $graph_id}]->
          (k:Keyword {graph_id: $graph_id})
          <-[:HAS_KEYWORD {graph_id: $graph_id}]-
          (o:Chunk {graph_id: $graph_id})
    WHERE main.id <> o.id
    RETURN o.text AS text, COUNT(DISTINCT k) AS score
    ORDER BY score DESC
    LIMIT $limit
    """

    try:
        with driver.session() as s:
            rows = s.run(
                query,
                {
                    "id": chunk_id,
                    "graph_id": graph_id,
                    "limit": limit
                }
            ).data()

        texts = [r["text"] for r in rows]
        print(f"[DEBUG] Overlap texts found: {len(texts)}")
        return texts

    except Exception as e:
        print("[WARN] Neo4j overlap fetch failed:", e)
        return []




# ------------------ LLM Agents ------------------

def question_agent(chunk_text):
    print("\n[DEBUG] Generating question from chunk")
    print("Chunk preview:", chunk_text[:200], "...")

    prompt = f"""
Create ONE HARD exam-level MCQ question from the text below.
Avoid definitions. Ask about limitation, implication, or condition.

TEXT:
{chunk_text}

Return strictly:
Question:
Answer:
"""
    resp = llm.invoke(prompt).content.strip()
    print("[DEBUG] LLM response:\n", resp)

    if "Answer:" not in resp:
        raise ValueError("Answer missing")

    q, a = resp.split("Answer:", 1)
    return q.replace("Question:", "").strip(), a.strip()


def option_agent(question, answer, overlap_texts):
    print("\n[DEBUG] Generating options")
    options = [answer]

    for ref in overlap_texts:
        prompt = f"""
Generate ONE tricky but incorrect option.

Rules:
- Similar wording to correct answer
- Partially true but wrong
- No giveaway words

QUESTION:
{question}

CORRECT ANSWER:
{answer}

REFERENCE:
{ref}

Return ONLY the option text.
"""
        opt = llm.invoke(prompt).content.strip()

        if opt.lower() != answer.lower():
            options.append(opt)

        if len(options) == 4:
            break

    print("[DEBUG] Options generated:", options)
    return options


# ------------------ Main Generator ------------------

def generate_mcqs(graph_id, limit=10):
    print("\n[DEBUG] Starting MCQ generation")
    mcqs = []

    chunks = fetch_chunks(graph_id)

    for chunk in chunks:
        print("\n==============================")
        print("[DEBUG] Processing chunk:", chunk["id"])

        if len(mcqs) == limit:
            break

        for attempt in range(MAX_TRIES_PER_CHUNK):
            print(f"[DEBUG] Attempt {attempt+1}/{MAX_TRIES_PER_CHUNK}")

            try:
                question, answer = question_agent(chunk["text"])

                overlaps = get_overlap_texts(
                    chunk["id"],
                    graph_id,
                    limit=3
                )

                if not overlaps:
                    print("[DEBUG] Using fallback overlaps")
                    overlaps = [chunk["text"]] * 3

                options = option_agent(question, answer, overlaps)

                if len(options) < 4:
                    continue

                if not not_easy(question, options):
                    continue

                mcqs.append({
                    "graph_id": graph_id,
                    "chunk_id": chunk["id"],
                    "question": question,
                    "options": options,
                    "answer": answer
                })

                print("[DEBUG] MCQ ACCEPTED ✅")
                break

            except Exception as e:
                print("[ERROR] Generation failed:", e)

    print("\n[DEBUG] MCQ generation completed")
    print("[DEBUG] Total MCQs generated:", len(mcqs))
    return mcqs

