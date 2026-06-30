"""Guideline search tool — wraps RAG retriever."""

from src.rag.retriever import GuidelineRetriever

_retriever: GuidelineRetriever | None = None


def get_retriever() -> GuidelineRetriever:
    global _retriever
    if _retriever is None:
        _retriever = GuidelineRetriever()
        _retriever.initialize()
    return _retriever


def search_clinical_guidelines(query: str, top_k: int = 3) -> list[dict]:
    results = get_retriever().retrieve(query, top_k=top_k)
    return [
        {
            "id": r.id,
            "title": r.title,
            "content": r.content,
            "score": round(r.score, 4),
            "source": r.source,
            "last_updated": r.last_updated,
        }
        for r in results
    ]
