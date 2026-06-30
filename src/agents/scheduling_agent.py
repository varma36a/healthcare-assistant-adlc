"""Scheduling Agent — proposes follow-up appointments."""

from src.tools.schedule_tool import propose_appointment

SPECIALTY_MAP = {
    "E11.9": "Internal Medicine",
    "I30.9": "Cardiology",
    "N39.0": "Internal Medicine",
    "M06.9": "Rheumatology",
    "I10": "Internal Medicine",
}


class SchedulingAgent:
    name = "SchedulingAgent"
    pattern = "Tool-calling"

    def run(self, patient_id: str, diagnosis: dict, red_flag: bool) -> dict:
        if red_flag:
            return {
                "agent": self.name,
                "status": "blocked",
                "reason": "RED FLAG — scheduling deferred until clinician review and escalation complete.",
                "requires_clinician_action": True,
            }

        if not diagnosis.get("differential"):
            return {"agent": self.name, "status": "skipped", "reason": "No diagnosis to schedule for."}

        top = diagnosis["differential"][0]
        specialty = SPECIALTY_MAP.get(top["icd10"])
        reason = f"Follow-up for {top['label']} ({top['icd10']})"

        proposal = propose_appointment(patient_id, reason, specialty=specialty)
        return {
            "agent": self.name,
            **proposal,
        }
