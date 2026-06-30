"""Shared helpers for the Streamlit dashboard."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.supervisor import SupervisorAgent, WorkflowResult
from src.config import GOLDEN_DATASET_PATH, GUIDELINES_PATH, KPI_THRESHOLDS
from src.rag.retriever import GuidelineRetriever
from src.tools.ehr_tool import list_patients, parse_lab_report, read_patient
from eval.run_eval import run_evaluation


def ensure_rag_ready() -> int:
    retriever = GuidelineRetriever()
    return retriever.initialize()


def load_golden_dataset() -> list[dict]:
    with open(GOLDEN_DATASET_PATH) as f:
        return json.load(f)


def load_guidelines() -> list[dict]:
    with open(GUIDELINES_PATH) as f:
        return json.load(f)


def run_workflow(patient_id: str) -> WorkflowResult:
    return SupervisorAgent().run(patient_id)


def workflow_to_dict(result: WorkflowResult) -> dict:
    if is_dataclass(result):
        return asdict(result)
    return result


def patient_badge(patient: dict) -> str:
    badges = []
    if patient.get("red_flag"):
        badges.append("RED FLAG")
    if patient.get("incomplete_records"):
        badges.append("INCOMPLETE")
    if patient.get("adversarial"):
        badges.append("ADVERSARIAL")
    return " · ".join(badges) if badges else "Standard"
