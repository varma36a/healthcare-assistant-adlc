#!/usr/bin/env python3
"""Healthcare Assistant — main CLI runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.supervisor import SupervisorAgent
from src.rag.retriever import GuidelineRetriever
from src.tools.ehr_tool import list_patients


def cmd_init_rag():
    retriever = GuidelineRetriever()
    count = retriever.initialize()
    print(f"✅ Vector store ready — {count} clinical guidelines indexed")


def cmd_list():
    patients = list_patients()
    print("\n📋 Dummy Patient Dataset:")
    print("-" * 60)
    for p in patients:
        flag = " 🚨 RED FLAG" if p.get("red_flag") else ""
        incomplete = " ⚠️ INCOMPLETE" if p.get("incomplete_records") else ""
        adv = " 🛡️ ADVERSARIAL" if p.get("adversarial") else ""
        print(f"  {p['patient_id']:20} {p['name']:25} {p.get('ground_truth_diagnosis_label', '')}{flag}{incomplete}{adv}")
    print()


def cmd_run(patient_id: str):
    print(f"\n🏥 Running clinical workflow for {patient_id}...")
    print("=" * 60)

    supervisor = SupervisorAgent()
    result = supervisor.run(patient_id)

    if result.red_flag:
        print("\n🚨 RED FLAG ESCALATION")
        for e in result.escalations:
            print(f"   → {e}")

    print("\n📝 SUMMARY (AI-DRAFT — requires clinician approval):")
    print(result.summary["summary"] if result.summary else "N/A")

    print("\n🔬 DIFFERENTIAL DIAGNOSIS (top 5):")
    for i, d in enumerate((result.diagnosis or {}).get("differential", []), 1):
        print(f"   {i}. {d['label']} ({d['icd10']}) — confidence: {d['confidence']}")

    print("\n📚 CLINICAL GUIDELINES (RAG):")
    for g in (result.guidelines or {}).get("guidelines", []):
        print(f"   [{g['id']}] {g['title']} (score: {g['score']})")

    print("\n📅 SCHEDULING:")
    sched = result.scheduling or {}
    print(f"   Status: {sched.get('status', 'N/A')}")
    if sched.get("message"):
        print(f"   {sched['message']}")

    print(f"\n⏱️  Latency: {result.latency_sec}s")
    print("\n📋 Audit Log:")
    for entry in result.audit_log:
        print(f"   • {entry}")
    print()


def cmd_eval():
    from eval.run_eval import run_evaluation
    report = run_evaluation()
    print("\n📊 Golden Dataset Evaluation (ADLC Phase 3/4)")
    print("=" * 60)
    for metric, value in report["metrics"].items():
        print(f"  {metric}: {value}")
    print("\n  Pass/Fail vs KPI thresholds:")
    for k, v in report["pass"].items():
        print(f"    {k}: {'✅ PASS' if v else '❌ FAIL'}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Healthcare Assistant — Agentic AI + RAG + VectorDB + MCP")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init-rag", help="Ingest clinical guidelines into vector store")
    sub.add_parser("list", help="List dummy patients")
    sub.add_parser("eval", help="Run golden dataset evaluation")

    run_parser = sub.add_parser("run", help="Run full clinical workflow for a patient")
    run_parser.add_argument("patient_id", help="Patient ID, e.g. P-001")

    args = parser.parse_args()

    if args.command == "init-rag":
        cmd_init_rag()
    elif args.command == "list":
        cmd_list()
    elif args.command == "run":
        cmd_run(args.patient_id)
    elif args.command == "eval":
        cmd_eval()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
