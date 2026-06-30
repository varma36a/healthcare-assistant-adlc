"""Report Analyst Agent — parses patient reports and labs."""

from src.tools.ehr_tool import parse_lab_report, read_patient


class ReportAnalystAgent:
    name = "ReportAnalyst"
    pattern = "ReAct"

    def run(self, patient_id: str) -> dict:
        patient = read_patient(patient_id)
        parsed_labs = parse_lab_report(patient)

        return {
            "agent": self.name,
            "patient_id": patient_id,
            "patient_name": patient["name"],
            "age": patient["age"],
            "gender": patient["gender"],
            "vitals": patient.get("vitals", {}),
            "medications": patient.get("medications", []),
            "conditions": patient.get("conditions", []),
            "allergies": patient.get("allergies", []),
            "notes": patient.get("notes", ""),
            "injection_warnings": patient.get("injection_warnings", []),
            "incomplete_records": patient.get("incomplete_records", False),
            "lab_analysis": parsed_labs,
            "red_flag": patient.get("red_flag", False),
        }
