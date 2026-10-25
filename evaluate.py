
import csv
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from src.retrieval import Retriever
from src.answer import generate_answer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "practice" / "questions.csv"
OUTPUT_FILE = BASE_DIR / "evaluation_results.csv"

client = genai.Client()
MODEL = "gemini-3.5-flash-lite"


def llm_only(question):
    prompt = f"""
You are a customer-support assistant for ZentroMart.
Answer the customer's question briefly and honestly.
Do not invent company policies. If you do not know, say so.

Customer question: {question}
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text or ""


def terms_from_field(value):
    return [
        term.strip().lower()
        for term in (value or "").split("/")
        if term.strip()
    ]



def evaluate_terms(answer, must_include, must_not_include):
    normalized = answer.lower()

    def groups(value):
        return [
            [term.strip().lower() for term in group.split("/") if term.strip()]
            for group in (value or "").split(";")
            if group.strip()
        ]

    required_groups = groups(must_include)
    forbidden_groups = groups(must_not_include)

    # Every semicolon-separated group must match at least one
    # slash-separated alternative.
    required_pass = all(
        any(term in normalized for term in alternatives)
        for alternatives in required_groups
    )

    # Any forbidden phrase appearing in the answer is a failure.
    forbidden_pass = not any(
        term in normalized
        for alternatives in forbidden_groups
        for term in alternatives
    )

    return required_pass, forbidden_pass

def main():
    retriever = Retriever()

    with QUESTIONS_FILE.open(encoding="utf-8-sig", newline="") as f:
        questions = list(csv.DictReader(f))

    results = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        print(f"[{index}/{len(questions)}] {item['id']}: {question}")

        try:
            baseline = llm_only(question)
        except Exception as exc:
            baseline = f"ERROR: {exc}"

        try:
            chunks = retriever.search(question, top_k=4)
            rag_answer = generate_answer(question, chunks)
            chunk_ids = "; ".join(
                str(chunk.get("section_id", ""))
                for chunk in chunks
            )
        except Exception as exc:
            rag_answer = f"ERROR: {exc}"
            chunk_ids = ""

        for method, answer in (
            ("LLM-only", baseline),
            ("RAG", rag_answer),
        ):
            include_ok, exclude_ok = evaluate_terms(
                answer,
                item.get("must_include", ""),
                item.get("must_not_include", ""),
            )

            results.append({
                "id": item["id"],
                "intent": item["intent"],
                "answerable": item["answerable"],
                "method": method,
                "question": question,
                "answer": answer,
                "must_include_pass": include_ok,
                "must_not_include_pass": exclude_ok,
                "both_checks_pass": include_ok and exclude_ok,
                "gold_evidence": item.get("gold_evidence", ""),
                "retrieved_sections": chunk_ids if method == "RAG" else "",
                "reference_answer": item.get("reference_answer", ""),
            })

    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to: {OUTPUT_FILE}")

    for method in ("LLM-only", "RAG"):
    subset = [r for r in results if r["method"] == method]
    total = len(subset)
    passed = sum(r["both_checks_pass"] for r in subset)

    print(
        f"{method}: {passed}/{total} passed both term checks "
        f"({passed / total:.1%})"
    )

if __name__ == "__main__":
    main()