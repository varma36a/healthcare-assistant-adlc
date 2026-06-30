"""History Summarizer Agent — drafts structured clinical summary."""

from src.guardrails import detect_prompt_injection


class HistorySummarizerAgent:
    name = "HistorySummarizer"
    pattern = "Single-shot + context"

    def run(self, report: dict) -> dict:
        vitals = report.get("vitals", {})
        labs = report.get("lab_analysis", {})
        findings = labs.get("findings", {})

        facts = []
        demographics = f"{report['age']}{report['gender'][0]} with {', '.join(report.get('conditions', []) or ['no known conditions'])}"
        facts.append(demographics)

        if vitals.get("bmi"):
            facts.append(f"BMI {vitals['bmi']}")
        if vitals.get("bp"):
            facts.append(f"BP {vitals['bp']}")
        if vitals.get("temp_f"):
            facts.append(f"Temp {vitals['temp_f']}F")
            if vitals["temp_f"] > 100:
                facts.append("fever")

        notes = report.get("notes", "").lower()
        if "thirst" in notes or "urination" in notes:
            facts.append("polyuria/polydipsia")
        if "chest pain" in notes:
            facts.append("chest pain")
        if "confusion" in notes:
            facts.append("acute confusion")
        if "stiffness" in notes:
            facts.append("morning stiffness")
        if "headache" in notes:
            facts.append("headaches")
        if "joint pain" in notes or "joint" in notes:
            facts.append("joint pain")
        if "urinary" in notes or "urination" in notes:
            facts.append("urinary symptoms")

        if labs.get("status") == "missing":
            facts.append("labs outdated/missing — incomplete records")
        else:
            if "hba1c" in findings:
                facts.append(f"HbA1c {findings['hba1c']}%")
            if "fasting_glucose" in findings:
                facts.append(f"fasting glucose {findings['fasting_glucose']} mg/dL")
            if "troponin" in findings:
                val = findings["troponin"]
                status = "normal" if val < 0.04 else "elevated"
                facts.append(f"troponin {val} ng/mL ({status})")
            if "ecg" in findings:
                facts.append(f"ECG: {findings['ecg']}")
            if "crp" in findings:
                val = findings["crp"]
                status = "elevated" if val > 3 else "normal"
                facts.append(f"CRP {val} mg/L ({status})")
            if "urinalysis" in findings:
                facts.append(f"urinalysis: {findings['urinalysis']}")
            if "anti_ccp" in findings:
                facts.append(f"anti-CCP {findings['anti_ccp']} U/mL")
            if "rf" in findings:
                facts.append(f"RF {findings['rf']} IU/mL")

            if "wbc" in findings:
                val = findings["wbc"]
                status = "elevated" if val > 11 else "normal"
                facts.append(f"WBC {val} K/uL ({status})")

        summary = f"CLINICAL SUMMARY (AI-DRAFT — REQUIRES CLINICIAN APPROVAL):\n"
        summary += f"Patient: {report['patient_name']} ({report['patient_id']})\n"
        summary += "- " + "\n- ".join(facts)

        warnings = list(report.get("injection_warnings", []))
        if detect_prompt_injection(report.get("notes", "")):
            warnings.append("Prompt injection detected and redacted from notes")

        return {
            "agent": self.name,
            "summary": summary,
            "facts": facts,
            "warnings": warnings,
            "requires_approval": True,
        }
