"""Guideline Retrieval Agent — RAG over clinical guidelines."""

from src.tools.guideline_tool import search_clinical_guidelines


class GuidelineRetrievalAgent:
    name = "GuidelineRetrieval"
    pattern = "RAG-only"

    def run(self, diagnosis: dict, summary: dict) -> dict:
        if not diagnosis.get("differential"):
            return {"agent": self.name, "guidelines": [], "message": "No diagnosis to lookup."}

        top = diagnosis["differential"][0]
        query = f"{top['label']} {top['icd10']} management treatment guidelines"
        results = search_clinical_guidelines(query, top_k=2)

        return {
            "agent": self.name,
            "query": query,
            "guidelines": results,
            "citations": [r["id"] for r in results],
            "formatted": "\n\n".join(
                f"[{r['id']}] {r['title']}\n{r['content']}" for r in results
            ),
        }
