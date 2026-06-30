"""Diagnosis Support Agent — suggests ranked differential diagnoses."""

# Rule-based differential engine keyed on lab flags and symptoms
DIFFERENTIAL_RULES = [
    {
        "icd10": "E11.9",
        "label": "Type 2 Diabetes Mellitus",
        "triggers": ["hyperglycemia", "elevated_hba1c", "polyuria/polydipsia"],
        "weight": 0.92,
    },
    {
        "icd10": "R73.03",
        "label": "Prediabetes",
        "triggers": ["elevated_hba1c", "polyuria/polydipsia"],
        "weight": 0.45,
    },
    {
        "icd10": "I30.9",
        "label": "Acute Pericarditis",
        "triggers": ["chest pain", "inflammation"],
        "weight": 0.88,
    },
    {
        "icd10": "I20.9",
        "label": "Angina Pectoris",
        "triggers": ["chest pain"],
        "weight": 0.35,
    },
    {
        "icd10": "F41.1",
        "label": "Generalized Anxiety Disorder",
        "triggers": ["chest pain"],
        "weight": 0.10,
    },
    {
        "icd10": "N39.0",
        "label": "Urinary Tract Infection",
        "triggers": ["possible_uti", "acute confusion", "fever"],
        "weight": 0.90,
    },
    {
        "icd10": "F05",
        "label": "Delirium",
        "triggers": ["acute confusion", "fever"],
        "weight": 0.55,
    },
    {
        "icd10": "M06.9",
        "label": "Rheumatoid Arthritis",
        "triggers": ["positive_anti_ccp", "morning stiffness"],
        "weight": 0.91,
    },
    {
        "icd10": "I10",
        "label": "Essential Hypertension",
        "triggers": ["headaches"],
        "weight": 0.75,
    },
]


class DiagnosisSupportAgent:
    name = "DiagnosisSupport"
    pattern = "ReAct + RAG"

    def run(self, report: dict, summary: dict) -> dict:
        lab_flags = set(report.get("lab_analysis", {}).get("flags", []))
        facts = [f.lower() for f in summary.get("facts", [])]
        fact_text = " ".join(facts)

        scored = []
        for rule in DIFFERENTIAL_RULES:
            score = 0.0
            matched = []
            for trigger in rule["triggers"]:
                if trigger in lab_flags or trigger in fact_text:
                    score += rule["weight"]
                    matched.append(trigger)
            if score > 0:
                scored.append({
                    "icd10": rule["icd10"],
                    "label": rule["label"],
                    "confidence": min(round(score, 2), 0.99),
                    "evidence": matched,
                })

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        top5 = scored[:5]

        return {
            "agent": self.name,
            "differential": top5,
            "disclaimer": "AI-GENERATED DIFFERENTIAL — CLINICIAN MUST CONFIRM FINAL DIAGNOSIS",
            "requires_approval": True,
        }
