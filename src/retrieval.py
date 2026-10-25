
from pathlib import Path
import re

import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "kb"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents():
    documents = []

    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata = {
            "source": path.name,
            "status": "",
            "effective_from": "",
        }

        for key in ("status", "effective_from"):
            match = re.search(
                rf"^{key}\s*:\s*(.+)$",
                text,
                re.IGNORECASE | re.MULTILINE,
            )
            if match:
                metadata[key] = match.group(1).strip()

        sections = re.split(
            r"(?=^#{1,3}\s+\[[A-Z0-9_-]+\])",
            text,
            flags=re.MULTILINE,
        )

        for section in sections:
            section = section.strip()
            if not section:
                continue

            match = re.search(
                r"^#{1,3}\s+\[([A-Z0-9_-]+)\]\s*(.*)$",
                section,
                re.MULTILINE,
            )

            if match:
                section_id = match.group(1)
                title = match.group(2).strip()
            else:
                section_id = "GENERAL"
                title = path.stem

            documents.append({
                **metadata,
                "section_id": section_id,
                "title": title,
                "text": section,
            })

    return documents


class Retriever:
    def __init__(self):
        self.documents = load_documents()

        if not self.documents:
            raise RuntimeError(f"No documents found in {KB_DIR}")

        self.model = SentenceTransformer(MODEL_NAME)
        self.embeddings = self.model.encode(
            [d["text"] for d in self.documents],
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def search(self, query, top_k=4):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]

        scores = self.embeddings @ query_embedding
        indices = np.argsort(scores)[::-1][:top_k]

        return [
            {
                **self.documents[int(i)],
                "score": float(scores[i]),
            }
            for i in indices
        ]
