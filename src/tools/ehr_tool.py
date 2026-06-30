"""EHR tool — read dummy patient records."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import PATIENTS_DIR
from src.guardrails import sanitize_clinical_notes


def list_patients() -> list[dict]:
    patients = []
    for path in sorted(PATIENTS_DIR.glob("*.json")):
        with open(path) as f:
            patients.append(json.load(f))
    return patients


def read_patient(patient_id: str) -> dict:
    for path in PATIENTS_DIR.glob("*.json"):
        with open(path) as f:
            data = json.load(f)
        if data["patient_id"] == patient_id:
            notes = data.get("notes", "")
            cleaned_notes, warnings = sanitize_clinical_notes(notes)
            data = {**data, "notes": cleaned_notes, "injection_warnings": warnings}
            return data
    raise ValueError(f"Patient {patient_id} not found")


def parse_lab_report(patient: dict) -> dict:
    """Extract structured lab findings from patient record."""
    labs = patient.get("lab_report")
    if labs is None:
        return {
            "status": "missing",
            "message": "No lab report available. Flag as incomplete — do NOT invent values.",
            "findings": {},
        }

    findings = {}
    flags = []

    if "fasting_glucose_mg_dl" in labs:
        val = labs["fasting_glucose_mg_dl"]
        findings["fasting_glucose"] = val
        if val >= 126:
            flags.append("hyperglycemia")

    if "hba1c_percent" in labs:
        val = labs["hba1c_percent"]
        findings["hba1c"] = val
        if val >= 6.5:
            flags.append("elevated_hba1c")

    if "troponin_i_ng_ml" in labs:
        findings["troponin"] = labs["troponin_i_ng_ml"]

    if "crp_mg_l" in labs:
        val = labs["crp_mg_l"]
        findings["crp"] = val
        if val > 3:
            flags.append("inflammation")

    if "ecg_summary" in labs:
        findings["ecg"] = labs["ecg_summary"]

    if "urinalysis" in labs:
        findings["urinalysis"] = labs["urinalysis"]
        flags.append("possible_uti")

    if "anti_ccp_u_ml" in labs:
        findings["anti_ccp"] = labs["anti_ccp_u_ml"]
        if labs["anti_ccp_u_ml"] > 20:
            flags.append("positive_anti_ccp")

    if "rf_iu_ml" in labs:
        findings["rf"] = labs["rf_iu_ml"]

    if "wbc_k_ul" in labs:
        val = labs["wbc_k_ul"]
        findings["wbc"] = val
        if val > 11:
            flags.append("leukocytosis")

    return {"status": "available", "findings": findings, "flags": flags, "raw": labs}
