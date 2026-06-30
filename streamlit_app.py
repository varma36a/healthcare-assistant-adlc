"""Streamlit dashboard for Healthcare Assistant."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from eval.run_eval import run_evaluation
from src.agents.supervisor import SupervisorAgent
from src.config import GOLDEN_DATASET_PATH, GUIDELINES_PATH, KPI_THRESHOLDS
from src.rag.retriever import GuidelineRetriever
from src.tools.ehr_tool import list_patients, parse_lab_report, read_patient
from src.tools.schedule_tool import get_available_slots

st.set_page_config(
    page_title="Healthcare Assistant Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

AGENT_COLORS = {
    "Supervisor": "#6366f1",
    "ReportAnalyst": "#0ea5e9",
    "HistorySummarizer": "#14b8a6",
    "DiagnosisSupport": "#f59e0b",
    "GuidelineRetrieval": "#8b5cf6",
    "SchedulingAgent": "#ec4899",
}


@st.cache_resource
def get_supervisor():
    return SupervisorAgent()


@st.cache_resource
def init_vector_store():
    retriever = GuidelineRetriever()
    count = retriever.initialize()
    return retriever, count


@st.cache_data
def load_golden_dataset():
    with open(GOLDEN_DATASET_PATH) as f:
        return json.load(f)


@st.cache_data
def load_guidelines():
    with open(GUIDELINES_PATH) as f:
        return json.load(f)


@st.cache_data(ttl=60)
def run_full_evaluation():
    return run_evaluation()


def metric_card(label: str, value: str, delta: str | None = None, pass_ok: bool | None = None):
    if pass_ok is True:
        st.success(f"**{label}:** {value} ✅")
    elif pass_ok is False:
        st.error(f"**{label}:** {value} ❌")
    else:
        st.info(f"**{label}:** {value}")


def render_sidebar():
    st.sidebar.title("🏥 Healthcare Assistant")
    st.sidebar.caption("Agentic AI + RAG + VectorDB + MCP")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Clinical Workflow",
            "Evaluation Metrics",
            "Patient Registry",
            "RAG Explorer",
            "ADLC Phases",
        ],
    )
    st.sidebar.divider()
    _, count = init_vector_store()
    st.sidebar.metric("Guidelines indexed", count)
    st.sidebar.metric("Dummy patients", len(list_patients()))
    st.sidebar.metric("Golden test cases", len(load_golden_dataset()))
    return page


def page_overview():
    st.title("Dashboard Overview")
    st.caption("ADLC Healthcare Assistant — local metrics and system status")

    eval_report = run_full_evaluation()
    metrics = eval_report["metrics"]
    passed = eval_report["pass"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Summary Accuracy", f"{metrics['summary_accuracy']:.0%}", "≥ 96%")
    c2.metric("Recall@5", f"{metrics['recall_at_5']:.0%}", "≥ 85%")
    c3.metric("Hallucination Rate", f"{metrics['hallucination_rate']:.0%}", "< 2%")
    c4.metric("Cases Tested", metrics["cases_tested"])
    c5.metric("All KPIs", "PASS" if all(passed.values()) else "FAIL")

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("KPI Pass / Fail")
        rows = []
        for key, ok in passed.items():
            val = metrics[key]
            if key == "cases_tested":
                display = str(val)
                threshold = "—"
            elif key == "hallucination_rate":
                display = f"{val:.1%}"
                threshold = f"≤ {KPI_THRESHOLDS[key]:.0%}"
            else:
                display = f"{val:.1%}"
                threshold = f"≥ {KPI_THRESHOLDS[key]:.0%}"
            rows.append({
                "Metric": key.replace("_", " ").title(),
                "Result": display,
                "Threshold": threshold,
                "Status": "✅ PASS" if ok else "❌ FAIL",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.subheader("Architecture")
        st.code(
            "Supervisor (Plan-and-Execute)\n"
            "  ├── Report Analyst      → EHR Tool\n"
            "  ├── History Summarizer  → Context Assembly\n"
            "  ├── Diagnosis Support   → Differential Engine\n"
            "  ├── Guideline Retrieval → RAG + VectorDB\n"
            "  └── Scheduling Agent    → Calendar API",
            language="text",
        )

    with right:
        st.subheader("System Status")
        all_pass = all(passed.values())
        st.success("All KPIs passing" if all_pass else "Some KPIs failing")
        st.markdown("**Stack**")
        st.markdown("- Multi-agent orchestration")
        st.markdown("- TF-IDF VectorDB")
        st.markdown("- Clinical guideline RAG")
        st.markdown("- MCP server (8 tools)")
        st.markdown("- Golden dataset eval")

        st.subheader("Quick Run")
        patient_id = st.selectbox(
            "Patient",
            [p["patient_id"] for p in list_patients()],
            key="overview_patient",
        )
        if st.button("Run Workflow", type="primary", use_container_width=True):
            st.session_state["selected_patient"] = patient_id
            st.session_state["page"] = "Clinical Workflow"
            st.rerun()


def page_clinical_workflow():
    st.title("Clinical Workflow")
    st.caption("Run the full multi-agent pipeline for a dummy patient")

    patients = list_patients()
    labels = {
        p["patient_id"]: f"{p['patient_id']} — {p['name']} ({p.get('ground_truth_diagnosis_label', '')})"
        for p in patients
    }

    default = st.session_state.get("selected_patient", "P-001")
    default_idx = list(labels.keys()).index(default) if default in labels else 0

    patient_id = st.selectbox(
        "Select patient",
        list(labels.keys()),
        format_func=lambda x: labels[x],
        index=default_idx,
    )

    if st.button("▶ Run Clinical Workflow", type="primary"):
        with st.spinner("Running multi-agent pipeline..."):
            supervisor = get_supervisor()
            result = supervisor.run(patient_id)
            patient = read_patient(patient_id)
            st.session_state["workflow_result"] = result
            st.session_state["workflow_patient"] = patient

    if "workflow_result" not in st.session_state:
        st.info("Select a patient and click **Run Clinical Workflow** to see results.")
        return

    result = st.session_state["workflow_result"]
    patient = st.session_state.get("workflow_patient", read_patient(patient_id))

    if result.patient_id != patient_id:
        supervisor = get_supervisor()
        result = supervisor.run(patient_id)
        patient = read_patient(patient_id)
        st.session_state["workflow_result"] = result
        st.session_state["workflow_patient"] = patient

    # Header metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Patient", patient["name"])
    m2.metric("Latency", f"{result.latency_sec}s")
    m3.metric("Red Flag", "YES" if result.red_flag else "No")
    m4.metric("Steps", len(result.steps))

    if result.red_flag:
        st.error("🚨 RED FLAG — Immediate clinician review required. Scheduling blocked.")

    for esc in result.escalations:
        st.warning(f"⚠️ {esc}")

    st.divider()

    # Pipeline steps
    st.subheader("Agent Pipeline")
    step_cols = st.columns(len(result.steps))
    for col, step in zip(step_cols, result.steps):
        agent = step["agent"]
        color = AGENT_COLORS.get(agent, "#64748b")
        col.markdown(
            f"<div style='background:{color}22;border-left:4px solid {color};"
            f"padding:12px;border-radius:8px;'>"
            f"<b>Step {step['step']}</b><br>{agent}<br>"
            f"<small>{step['output']}</small></div>",
            unsafe_allow_html=True,
        )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Summary", "Diagnosis", "Guidelines (RAG)", "Scheduling", "Patient Data", "Audit Log",
    ])

    with tab1:
        st.markdown("#### AI-Draft Summary")
        st.warning("Requires clinician approval before chart entry")
        if result.summary:
            st.text(result.summary.get("summary", ""))
            st.markdown("**Extracted facts**")
            st.write(result.summary.get("facts", []))
            if result.summary.get("warnings"):
                st.error(f"Warnings: {result.summary['warnings']}")

    with tab2:
        st.markdown("#### Differential Diagnosis (Top 5)")
        st.warning("Clinician must confirm final diagnosis")
        diff = (result.diagnosis or {}).get("differential", [])
        if diff:
            df = pd.DataFrame(diff)
            df["confidence"] = df["confidence"].apply(lambda x: f"{x:.0%}")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.bar_chart(pd.DataFrame(diff).set_index("label")["confidence"])
        else:
            st.info("No differential generated.")

        gt = patient.get("ground_truth_diagnosis_label", "")
        if gt:
            in_top5 = any(d["icd10"] == patient.get("ground_truth_diagnosis") for d in diff)
            st.markdown(f"**Ground truth:** {gt} ({patient.get('ground_truth_diagnosis')})")
            st.success("Correct diagnosis in top 5 ✅" if in_top5 else "Not in top 5 ❌")

    with tab3:
        st.markdown("#### Clinical Guidelines (RAG + VectorDB)")
        guidelines = (result.guidelines or {}).get("guidelines", [])
        if guidelines:
            for g in guidelines:
                with st.expander(f"[{g['id']}] {g['title']} — score {g['score']:.4f}"):
                    st.markdown(f"**Source:** {g['source']} | **Updated:** {g['last_updated']}")
                    st.write(g["content"])
        else:
            st.info("No guidelines retrieved.")
        if result.guidelines and result.guidelines.get("query"):
            st.caption(f"RAG query: `{result.guidelines['query']}`")

    with tab4:
        st.markdown("#### Follow-up Scheduling")
        sched = result.scheduling or {}
        status = sched.get("status", "unknown")
        if status == "blocked":
            st.error(f"Status: **{status}** — {sched.get('reason', '')}")
        elif status == "proposed":
            st.success(f"Status: **{status}**")
            st.info(sched.get("message", ""))
            slot = sched.get("slot", {})
            if slot:
                st.json(slot)
            st.warning("Booking requires clinician approval")
        else:
            st.write(sched)

    with tab5:
        st.markdown("#### Raw Patient Record")
        col_a, col_b = st.columns(2)
        with col_a:
            st.json({
                "patient_id": patient["patient_id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "conditions": patient.get("conditions"),
                "medications": patient.get("medications"),
                "allergies": patient.get("allergies"),
                "vitals": patient.get("vitals"),
            })
        with col_b:
            labs = parse_lab_report(patient)
            st.markdown("**Lab analysis**")
            st.json(labs)
            st.markdown("**Clinical notes**")
            st.text(patient.get("notes", ""))

    with tab6:
        st.markdown("#### Audit Log")
        for entry in result.audit_log:
            st.markdown(f"- {entry}")


def page_evaluation():
    st.title("Evaluation Metrics")
    st.caption("Golden dataset regression — ADLC Phase 3 / 4 / 5")

    if st.button("🔄 Re-run Evaluation", type="primary"):
        run_full_evaluation.clear()
        st.cache_data.clear()
        st.rerun()

    report = run_full_evaluation()
    metrics = report["metrics"]
    passed = report["pass"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Summary Accuracy", f"{metrics['summary_accuracy']:.1%}",
              delta="PASS" if passed["summary_accuracy"] else "FAIL",
              delta_color="normal" if passed["summary_accuracy"] else "inverse")
    c2.metric("Recall@5", f"{metrics['recall_at_5']:.1%}",
              delta="PASS" if passed["recall_at_5"] else "FAIL",
              delta_color="normal" if passed["recall_at_5"] else "inverse")
    c3.metric("Hallucination", f"{metrics['hallucination_rate']:.1%}",
              delta="PASS" if passed["hallucination_rate"] else "FAIL",
              delta_color="normal" if passed["hallucination_rate"] else "inverse")
    c4.metric("Cases", metrics["cases_tested"])

    st.divider()

    # Chart
    chart_df = pd.DataFrame({
        "Metric": ["Summary Accuracy", "Recall@5", "Hallucination Rate"],
        "Actual": [
            metrics["summary_accuracy"],
            metrics["recall_at_5"],
            metrics["hallucination_rate"],
        ],
        "Threshold": [
            KPI_THRESHOLDS["summary_accuracy"],
            KPI_THRESHOLDS["recall_at_5"],
            KPI_THRESHOLDS["hallucination_rate"],
        ],
    })
    st.subheader("Actual vs Threshold")
    st.bar_chart(chart_df.set_index("Metric"))

    st.subheader("Per-Case Results")
    case_rows = []
    for case in report["cases"]:
        facts = case.get("summary_facts", [])
        facts_found = sum(1 for f in facts if f["found"])
        facts_total = len(facts)
        case_rows.append({
            "Case": case["case_id"],
            "Patient": case["patient_id"],
            "Summary Facts": f"{facts_found}/{facts_total}",
            "Recall@5": "✅" if case.get("recall_at_5") else "❌",
            "Red Flag": "✅" if case.get("red_flag_correct") else "❌",
            "Schedule": "✅" if case.get("schedule_ok") else "❌",
            "Guideline": "✅" if case.get("guideline_found") else "❌",
            "Hallucination": "❌ YES" if case.get("hallucination") else "✅ No",
            "Latency (s)": case.get("latency_sec", 0),
        })
    st.dataframe(pd.DataFrame(case_rows), use_container_width=True, hide_index=True)

    st.subheader("Fact-Level Detail")
    for case in report["cases"]:
        with st.expander(f"{case['case_id']} — {case['patient_id']}"):
            for fact in case.get("summary_facts", []):
                icon = "✅" if fact["found"] else "❌"
                st.markdown(f"{icon} `{fact['fact']}`")


def page_patient_registry():
    st.title("Patient Registry")
    st.caption("Dummy dataset — 6 fictional patients")

    patients = list_patients()
    rows = []
    for p in patients:
        rows.append({
            "ID": p["patient_id"],
            "Name": p["name"],
            "Age": p["age"],
            "Gender": p["gender"],
            "Diagnosis": p.get("ground_truth_diagnosis_label", ""),
            "ICD-10": p.get("ground_truth_diagnosis", ""),
            "Red Flag": "🚨" if p.get("red_flag") else "",
            "Incomplete": "⚠️" if p.get("incomplete_records") else "",
            "Adversarial": "🛡️" if p.get("adversarial") else "",
            "Has Labs": "Yes" if p.get("lab_report") else "No",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("Patient Detail")
    selected = st.selectbox("View patient", [p["patient_id"] for p in patients])
    patient = read_patient(selected)
    st.json(patient)


def page_rag_explorer():
    st.title("RAG Explorer")
    st.caption("Search clinical guidelines vector store")

    retriever, count = init_vector_store()
    st.metric("Indexed guidelines", count)

    default_queries = [
        "type 2 diabetes management HbA1c",
        "chest pain pericarditis ECG",
        "urinary tract infection elderly delirium",
        "rheumatoid arthritis DMARD",
        "hypertension management labs",
    ]
    query = st.text_input("Search query", value=default_queries[0])
    top_k = st.slider("Top K results", 1, 5, 3)

    if st.button("Search", type="primary") or query:
        results = retriever.retrieve(query, top_k=top_k)
        if not results:
            st.warning("No results found.")
            return

        for r in results:
            with st.expander(f"[{r.id}] {r.title} — score {r.score:.4f}", expanded=True):
                st.markdown(f"**Source:** {r.source} | **Updated:** {r.last_updated}")
                st.progress(min(r.score, 1.0))
                st.write(r.content)

    st.divider()
    st.subheader("Full Guidelines Corpus")
    guidelines = load_guidelines()
    st.dataframe(
        pd.DataFrame([{
            "ID": g["id"],
            "Title": g["title"],
            "Specialty": g["specialty"],
            "Condition": g["condition"],
            "Updated": g["last_updated"],
        } for g in guidelines]),
        use_container_width=True,
        hide_index=True,
    )


def page_adlc():
    st.title("ADLC Phases")
    st.caption("Agentic Development Lifecycle applied to Healthcare Assistant")

    phases = [
        ("Phase 1 — Scope", "KPIs, constraints, human–agent model", "✅ config.py, dummy dataset"),
        ("Phase 2 — Architecture", "Multi-agent, RAG, VectorDB, MCP", "✅ src/agents/, mcp_server/"),
        ("Phase 3 — PoV", "Golden dataset, go/no-go gate", "✅ eval/run_eval.py"),
        ("Phase 4 — Build", "Continuous eval on every change", "✅ CI-ready eval suite"),
        ("Phase 5 — Testing", "Red-team, incomplete, adversarial cases", "✅ G-005, G-006 in golden set"),
        ("Phase 6 — Deploy", "CLI + Streamlit + MCP", "✅ This dashboard"),
        ("Phase 7 — Govern", "Guideline refresh, regression", "✅ init-rag + eval loop"),
    ]

    for title, desc, status in phases:
        with st.expander(f"{title}: {desc}", expanded=False):
            st.markdown(status)

    st.subheader("Human–Agent Responsibility")
    st.markdown("""
| Agent can do | Requires approval | Never |
|---|---|---|
| Parse reports | Final diagnosis | Prescribe |
| Draft summaries | Patient comms | Auto-book |
| Retrieve guidelines | Follow-up confirm | Override clinician |
| Suggest differentials | Chart finalization | Unauthorized access |
| Propose appointments | | |
| Flag red flags | | |
    """)

    st.subheader("Available Appointment Slots")
    slots = get_available_slots(limit=5)
    if slots:
        st.dataframe(pd.DataFrame(slots), use_container_width=True, hide_index=True)


def main():
    page = render_sidebar()
    if st.session_state.get("page") == "Clinical Workflow":
        page = "Clinical Workflow"
        del st.session_state["page"]

    pages = {
        "Overview": page_overview,
        "Clinical Workflow": page_clinical_workflow,
        "Evaluation Metrics": page_evaluation,
        "Patient Registry": page_patient_registry,
        "RAG Explorer": page_rag_explorer,
        "ADLC Phases": page_adlc,
    }
    pages[page]()


if __name__ == "__main__":
    main()
