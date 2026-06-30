"""Golden dataset evaluation — ADLC Phase 3/4/5 validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.supervisor import SupervisorAgent
from src.config import GOLDEN_DATASET_PATH, KPI_THRESHOLDS


def _fact_in_summary(fact: str, summary: dict) -> bool:
    text = summary.get("summary", "").lower() + " ".join(summary.get("facts", [])).lower()
    fact_lower = fact.lower()
    if fact_lower in text:
        return True
    # Token-based match for compound facts like "troponin normal" or "CRP elevated"
    tokens = fact_lower.split()
    if len(tokens) >= 2:
        return all(t in text for t in tokens)
    return False


def _diagnosis_in_top5(icd10: str, diagnosis: dict) -> bool:
    return any(d["icd10"] == icd10 for d in diagnosis.get("differential", []))


def _check_hallucination(patient_id: str, summary: dict) -> bool:
    """Returns True if hallucination detected (invented lab values for incomplete records)."""
    if patient_id != "P-005":
        return False
    text = summary.get("summary", "").lower()
    invented_markers = ["hba1c", "glucose", "creatinine", "egfr"]
    return any(m in text for m in invented_markers) and "missing" not in text and "outdated" not in text


def run_evaluation() -> dict:
    with open(GOLDEN_DATASET_PATH) as f:
        golden = json.load(f)

    supervisor = SupervisorAgent()
    results = []
    summary_hits = 0
    summary_total = 0
    recall_hits = 0
    hallucinations = 0

    for case in golden:
        wf = supervisor.run(case["patient_id"])
        case_result = {
            "case_id": case["case_id"],
            "patient_id": case["patient_id"],
            "latency_sec": wf.latency_sec,
        }

        # Summary accuracy
        fact_results = []
        for fact in case.get("expected_summary_facts", []):
            summary_total += 1
            found = _fact_in_summary(fact, wf.summary or {})
            if found:
                summary_hits += 1
            fact_results.append({"fact": fact, "found": found})
        case_result["summary_facts"] = fact_results

        # recall@5
        in_top5 = _diagnosis_in_top5(case["expected_diagnosis_icd10"], wf.diagnosis or {})
        if in_top5:
            recall_hits += 1
        case_result["recall_at_5"] = in_top5

        # Red flag
        case_result["red_flag_correct"] = wf.red_flag == case.get("expected_red_flag", False)

        # Scheduling
        sched_status = (wf.scheduling or {}).get("status", "")
        if case.get("expected_schedule"):
            case_result["schedule_ok"] = sched_status in ("proposed", "confirmed")
        else:
            case_result["schedule_ok"] = sched_status in ("blocked", "skipped")

        # Hallucination check
        if case.get("expected_no_hallucination"):
            hallucinated = _check_hallucination(case["patient_id"], wf.summary or {})
            if hallucinated:
                hallucinations += 1
            case_result["hallucination"] = hallucinated
        else:
            case_result["hallucination"] = False

        # Guideline citation
        citations = (wf.guidelines or {}).get("citations", [])
        expected_gid = case.get("expected_guideline_id")
        case_result["guideline_found"] = expected_gid in citations if expected_gid else True

        results.append(case_result)

    n = len(golden)
    summary_accuracy = summary_hits / summary_total if summary_total else 0
    recall_at_5 = recall_hits / n
    hallucination_rate = hallucinations / n

    report = {
        "metrics": {
            "summary_accuracy": round(summary_accuracy, 4),
            "recall_at_5": round(recall_at_5, 4),
            "hallucination_rate": round(hallucination_rate, 4),
            "cases_tested": n,
        },
        "thresholds": KPI_THRESHOLDS,
        "pass": {
            "summary_accuracy": summary_accuracy >= KPI_THRESHOLDS["summary_accuracy"],
            "recall_at_5": recall_at_5 >= KPI_THRESHOLDS["recall_at_5"],
            "hallucination_rate": hallucination_rate <= KPI_THRESHOLDS["hallucination_rate"],
        },
        "cases": results,
    }
    return report


def main():
    report = run_evaluation()
    print(json.dumps(report, indent=2))
    all_pass = all(report["pass"].values())
    print(f"\n{'✅ ALL KPIs PASSED' if all_pass else '❌ SOME KPIs FAILED'}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
