"""RAG retriever for clinical guidelines."""

from src.vector_store import GuidelineVectorStore, SearchResult


class GuidelineRetriever:
    def __init__(self):
        self.store = GuidelineVectorStore()

    def initialize(self) -> int:
        return self.store.ensure_ready()

    def retrieve(self, query: str, top_k: int = 3) -> list[SearchResult]:
        return self.store.search(query, top_k=top_k)

    def format_context(self, results: list[SearchResult]) -> str:
        if not results:
            return "No relevant guidelines found."
        parts = []
        for r in results:
            parts.append(
                f"[{r.id}] {r.title} (updated: {r.last_updated}, score: {r.score:.3f})\n{r.content}"
            )
        return "\n\n".join(parts)
