# Healthcare Assistant — Agentic AI + RAG + VectorDB + MCP

A **runnable** Healthcare Assistant built following the **Agentic Development Lifecycle (ADLC)**. Includes dummy patient dataset, multi-agent workflow, RAG over clinical guidelines, TF-IDF vector store, MCP server, and golden dataset evaluation.

**GitHub:** [healthcare-assistant-adlc](https://github.com/varma36a/healthcare-assistant-adlc)

## Capabilities

- Reading patient reports (EHR tool)
- Summarizing history (History Summarizer agent)
- Suggesting diagnoses with clinician oversight (Diagnosis Support agent)
- Finding clinical guidelines (RAG + VectorDB)
- Scheduling follow-ups (Scheduling agent, requires approval)

## Architecture

```
Supervisor Agent (Plan-and-Execute)
  ├── Report Analyst Agent (ReAct)        → EHR Tool
  ├── History Summarizer Agent            → Context assembly
  ├── Diagnosis Support Agent (ReAct+RAG) → Differential engine
  ├── Guideline Retrieval Agent (RAG)     → VectorDB (TF-IDF)
  └── Scheduling Agent (Tool-calling)     → Calendar API
```

## Quick Start

```bash
cd healthcare-assistant-adlc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py init-rag          # Index clinical guidelines into vector store
python main.py list              # List dummy patients
python main.py run P-001         # Run full workflow (diabetes case)
python main.py run P-002         # Red flag case (chest pain)
python main.py run P-006         # Adversarial / prompt injection case
python main.py eval              # Run golden dataset evaluation (6 cases)
```

## Dummy Patients

| ID | Name | Condition | Notes |
|---|---|---|---|
| P-001 | John Smith | Type 2 Diabetes | Full records |
| P-002 | Maria Garcia | Acute Pericarditis | RED FLAG |
| P-003 | Robert Chen | UTI + delirium | RED FLAG, elderly |
| P-004 | Sarah Johnson | Rheumatoid Arthritis | Full records |
| P-005 | James Wilson | Hypertension | Incomplete labs |
| P-006 | Adversarial Patient | Pericarditis | Prompt injection test |

## Project Structure

```
healthcare-assistant-adlc/
├── main.py                          # CLI runner
├── requirements.txt
├── data/
│   ├── patients/                    # 6 dummy patient JSON files
│   ├── guidelines/                  # Clinical guidelines corpus (RAG source)
│   ├── golden_dataset.json          # 6 test cases with ground truth
│   └── scheduling/schedule.json     # Dummy calendar
├── src/
│   ├── agents/                      # 5 sub-agents + supervisor
│   ├── tools/                       # EHR, schedule, guideline tools
│   ├── rag/retriever.py             # RAG retriever
│   ├── vector_store.py              # TF-IDF vector store
│   └── guardrails.py                # Safety + prompt injection detection
├── mcp_server/server.py             # MCP server (8 tools)
├── eval/run_eval.py                 # Golden dataset evaluation
└── docs/
    ├── HEALTHCARE_ASSISTANT_ADLC.md  # Full ADLC design (all 7 phases)
    └── ADLC_PHASE_WALKTHROUGH.md     # Phase walkthrough with dummy data
```

## MCP Server

Expose healthcare tools to Cursor or any MCP client. Copy `mcp_config.example.json` to your MCP config:

```json
{
  "mcpServers": {
    "healthcare-assistant": {
      "command": "/path/to/.venv/bin/python",
      "args": ["mcp_server/server.py"],
      "cwd": "/path/to/healthcare-assistant-adlc"
    }
  }
}
```

**MCP Tools:** `read_patient_record`, `parse_lab_report`, `search_clinical_guidelines`, `get_available_slots`, `propose_appointment`, `book_appointment`, `run_clinical_workflow`, `list_patients`

## Evaluation (ADLC Phase 3/4)

```bash
python main.py eval
```

| Metric | Threshold | Current |
|---|---|---|
| Summary accuracy | ≥ 96% | 100% |
| recall@5 | ≥ 85% | 100% |
| Hallucination rate | < 2% | 0% |

## Documentation

- [Full ADLC Design (all 7 phases)](docs/HEALTHCARE_ASSISTANT_ADLC.md)
- [Phase Walkthrough with Dummy Data](docs/ADLC_PHASE_WALKTHROUGH.md)

## ADLC Phases Covered

| Phase | What's in this repo |
|---|---|
| **1 — Scope** | KPIs in `src/config.py`, dummy dataset, responsibility model in docs |
| **2 — Architecture** | Multi-agent design, vector store, MCP server |
| **3 — PoV** | Golden dataset eval, go/no-go baselines |
| **4 — Build** | Full agent workflow, continuous eval suite |
| **5 — Testing** | 6 golden cases including adversarial + incomplete |
| **6 — Deploy** | CLI runner, MCP server, smoke test commands |
| **7 — Govern** | Eval regression, guideline refresh procedure |

## License

Documentation and demo code for learning purposes. Not for clinical use.
