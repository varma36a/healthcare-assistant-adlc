"""Lightweight TF-IDF vector store for clinical guideline RAG."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import GUIDELINES_PATH, VECTOR_STORE_DIR


@dataclass
class SearchResult:
    id: str
    title: str
    content: str
    score: float
    source: str
    last_updated: str


class GuidelineVectorStore:
    """TF-IDF vector store — no external embedding API required."""

    def __init__(self, store_dir: Path = VECTOR_STORE_DIR):
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._documents: list[dict] = []

    def _doc_text(self, doc: dict) -> str:
        return " ".join([
            doc.get("title", ""),
            doc.get("condition", ""),
            doc.get("specialty", ""),
            " ".join(doc.get("icd10", [])),
            doc.get("content", ""),
        ])

    def ingest(self, guidelines_path: Path = GUIDELINES_PATH) -> int:
        with open(guidelines_path) as f:
            self._documents = json.load(f)

        texts = [self._doc_text(d) for d in self._documents]
        self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self._matrix = self._vectorizer.fit_transform(texts)

        with open(self.store_dir / "store.pkl", "wb") as f:
            pickle.dump({
                "vectorizer": self._vectorizer,
                "matrix": self._matrix,
                "documents": self._documents,
            }, f)

        return len(self._documents)

    def load(self) -> bool:
        path = self.store_dir / "store.pkl"
        if not path.exists():
            return False
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._vectorizer = data["vectorizer"]
        self._matrix = data["matrix"]
        self._documents = data["documents"]
        return True

    def ensure_ready(self) -> int:
        if self.load():
            return len(self._documents)
        return self.ingest()

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if self._vectorizer is None or self._matrix is None:
            self.ensure_ready()

        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            doc = self._documents[idx]
            results.append(SearchResult(
                id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                score=float(scores[idx]),
                source=doc.get("source", ""),
                last_updated=doc.get("last_updated", ""),
            ))
        return results
