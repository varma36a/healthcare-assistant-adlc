"""Supervisor Agent — Plan-and-Execute orchestrator."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from src.agents.diagnosis_support import DiagnosisSupportAgent
from src.agents.guideline_agent import GuidelineRetrievalAgent
from src.agents.history_summarizer import HistorySummarizerAgent
from src.agents.report_analyst import ReportAnalystAgent
from src.agents.scheduling_agent import SchedulingAgent
from src.guardrails import check_red_flag


@dataclass
class WorkflowResult:
    patient_id: str
    steps: list[dict] = field(default_factory=list)
    summary: dict | None = None
    diagnosis: dict | None = None
    guidelines: dict | None = None
    scheduling: dict | None = None
    red_flag: bool = False
    escalations: list[str] = field(default_factory=list)
    latency_sec: float = 0.0
    audit_log: list[str] = field(default_factory=list)


class SupervisorAgent:
    name = "Supervisor"
    pattern = "Plan-and-Execute"

    def __init__(self):
        self.report_analyst = ReportAnalystAgent()
        self.summarizer = HistorySummarizerAgent()
        self.diagnosis_agent = DiagnosisSupportAgent()
        self.guideline_agent = GuidelineRetrievalAgent()
        self.scheduling_agent = SchedulingAgent()

    def run(self, patient_id: str, clinician_approved_booking: bool = False) -> WorkflowResult:
        start = time.time()
        result = WorkflowResult(patient_id=patient_id)

        # Step 1: Report Analyst
        report = self.report_analyst.run(patient_id)
        result.steps.append({"step": 1, "agent": "ReportAnalyst", "output": "Patient record parsed"})
        result.audit_log.append(f"ReportAnalyst read {patient_id}")

        # Step 2: Red flag check
        result.red_flag = check_red_flag(report) or report.get("red_flag", False)
        if result.red_flag:
            result.escalations.append("RED FLAG detected — immediate clinician review required")
            result.audit_log.append("RED FLAG escalation triggered")

        if report.get("injection_warnings"):
            result.escalations.append(f"Prompt injection blocked: {report['injection_warnings']}")
            result.audit_log.append("Prompt injection sanitized")

        # Step 3: History Summarizer
        summary = self.summarizer.run(report)
        result.summary = summary
        result.steps.append({"step": 2, "agent": "HistorySummarizer", "output": "Summary drafted"})
        result.audit_log.append("Summary drafted — pending clinician approval")

        # Step 4: Diagnosis Support
        diagnosis = self.diagnosis_agent.run(report, summary)
        result.diagnosis = diagnosis
        result.steps.append({"step": 3, "agent": "DiagnosisSupport", "output": f"Top: {diagnosis['differential'][0]['label'] if diagnosis['differential'] else 'none'}"})
        result.audit_log.append("Differential diagnosis proposed — pending clinician confirmation")

        # Step 5: Guideline Retrieval (RAG)
        guidelines = self.guideline_agent.run(diagnosis, summary)
        result.guidelines = guidelines
        result.steps.append({"step": 4, "agent": "GuidelineRetrieval", "output": f"Citations: {guidelines.get('citations', [])}"})
        result.audit_log.append(f"RAG retrieved guidelines: {guidelines.get('citations', [])}")

        # Step 6: Scheduling (blocked on red flags)
        scheduling = self.scheduling_agent.run(patient_id, diagnosis, result.red_flag)
        result.scheduling = scheduling
        result.steps.append({"step": 5, "agent": "SchedulingAgent", "output": scheduling.get("status", scheduling.get("message", ""))})
        result.audit_log.append(f"Scheduling: {scheduling.get('status')}")

        result.latency_sec = round(time.time() - start, 3)
        return result
