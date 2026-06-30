# Healthcare Assistant: Agentic AI System Design

**Framework:** Agentic Development Lifecycle (ADLC)  
**Use Case:** Clinical workflow assistant for reading reports, summarizing history, diagnosis support, guideline retrieval, and follow-up scheduling  
**Version:** 1.0  
**Date:** June 30, 2026

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Use Case & Capabilities](#use-case--capabilities)
3. [ADLC Overview](#adlc-overview)
4. [Phase 1 — Scope Framing & Problem Definition](#phase-1--scope-framing--problem-definition)
5. [Phase 2 — Agent Definition & Architecture](#phase-2--agent-definition--architecture)
6. [Phase 3 — Simulation & Proof of Value](#phase-3--simulation--proof-of-value)
7. [Phase 4 — Implementation & Evals](#phase-4--implementation--evals)
8. [Phase 5 — Testing](#phase-5--testing)
9. [Phase 6 — Agent Activation & Deployment](#phase-6--agent-activation--deployment)
10. [Phase 7 — Continuous Learning & Governance](#phase-7--continuous-learning--governance)
11. [Hypothesis Testing in ADLC](#hypothesis-testing-in-adlc)
12. [Appendix A — Hypothesis Register](#appendix-a--hypothesis-register)
13. [Appendix B — Phase Summary Matrix](#appendix-b--phase-summary-matrix)

---

## Executive Summary

This document describes the end-to-end design of a **Healthcare Assistant** agentic AI system using the **Agentic Development Lifecycle (ADLC)**. The agent augments clinical workflows — it does not replace clinician judgment.

**Core principle:** Uncertainty is explicit and managed at every phase. The agent operates within hard autonomy boundaries, validated continuously from golden dataset through production monitoring.

**Five capabilities:**

| Capability | Agent Role | Human Role |
|---|---|---|
| Reading patient reports | Parse PDFs, labs, imaging summaries | Validates completeness |
| Summarizing history | Draft structured summary | Approves before chart entry |
| Suggesting diagnoses | Ranked differential + rationale + citations | Final diagnosis authority |
| Finding clinical guidelines | Retrieve NICE/UpToDate/local protocols | Applies clinical judgment |
| Scheduling follow-ups | Propose slots, send reminders | Approves schedule changes |

---

## Use Case & Capabilities

### Problem Statement

Clinicians spend significant time on pre-visit chart preparation, manual history review, guideline lookup, and administrative scheduling. An agentic AI system can reduce this burden while maintaining strict clinical oversight, regulatory compliance, and auditability.

### Target Users

- Primary care physicians
- Specialists (cardiology, endocrinology, etc.)
- Clinical informatics teams
- Healthcare administrators (ROI, compliance)

### Out of Scope (v1)

- Autonomous prescribing
- Direct patient-facing diagnosis statements
- Autonomous treatment orders
- Cross-facility record access without explicit authorization

---

## ADLC Overview

The Agentic Development Lifecycle (ADLC) brings structure to agentic development by making uncertainty explicit and manageable. Clear quality thresholds, early validation with real data, and continuous monitoring replace guesswork.

```mermaid
flowchart LR
    P1["Phase 1\nScope & Constraints"] --> P2["Phase 2\nArchitecture & Design"]
    P2 --> P3["Phase 3\nPoV & Golden Dataset"]
    P3 -->|Go| P4["Phase 4\nBuild + Continuous Evals"]
    P3 -->|No-Go| STOP["Stop or Pivot"]
    P4 --> P5["Phase 5\nFormal Testing & Sign-off"]
    P5 --> P6["Phase 6\nControlled Deployment"]
    P6 --> P7["Phase 7\nContinuous Governance"]
    P7 -->|Improve| P4
```

### Why ADLC Differs from Traditional SDLC

| Dimension | Traditional SDLC | ADLC |
|---|---|---|
| Output determinism | Deterministic | Non-deterministic (LLM) |
| Testing timing | After build | During and after build |
| Human role | User | User + approver + accountability holder |
| Responsibility model | N/A | Explicit autonomy boundaries |
| Post-launch | Maintenance | Continuous governance required |

---

## Phase 1 — Scope Framing & Problem Definition

**Objective:** Translate a broad problem into a precisely scoped, governable agent opportunity.

### Core Activities

#### 1. Business Process Mapping

Map the end-to-end clinical workflow and where the agent sits:

```mermaid
flowchart LR
    A[Patient visit / referral] --> B[EHR intake]
    B --> C[Agent: ingest reports & labs]
    C --> D[Agent: summarize history]
    D --> E[Clinician review]
    E --> F[Agent: retrieve guidelines]
    F --> G[Agent: suggest differential diagnoses]
    G --> H[Clinician confirms / overrides]
    H --> I[Agent: schedule follow-up]
    I --> J[Documentation & audit log]
```

| Workflow Step | Agent Role | Human Role |
|---|---|---|
| Report ingestion | Parse PDFs, labs, imaging summaries | Validates completeness |
| History summary | Draft structured summary | Approves before chart entry |
| Diagnosis support | Ranked differential + rationale + citations | Final diagnosis authority |
| Guidelines lookup | Retrieve NICE/UpToDate/local protocols | Applies clinical judgment |
| Follow-up scheduling | Propose slots, send reminders | Approves schedule changes |

#### 2. Constraint Identification

| Constraint | Definition |
|---|---|
| **Regulatory** | HIPAA (US), GDPR (EU), FDA SaMD if diagnostic claims |
| **Unsafe autonomy zones** | Agent must **never** autonomously: prescribe, finalize diagnosis, modify orders, or contact patients without approval |
| **Acceptable error rates** | Summary factual accuracy ≥ 98%; diagnosis suggestions recall@5 ≥ 85% on golden set |
| **Risk tolerance** | Low — clinical harm is unacceptable; false negatives in red-flag conditions = zero tolerance |

#### 3. Business & Technical KPI Definition

| KPI | Target | Type |
|---|---|---|
| Pre-visit chart prep time | −40% | Business |
| Clinician time saved per encounter | 8–12 min | Business |
| Summary factual accuracy | ≥ 98% | Technical |
| Guideline citation accuracy | ≥ 95% | Technical |
| Hallucination rate (unsupported claims) | < 2% | Technical |
| P95 latency (summary generation) | < 8 sec | Technical |
| Escalation rate (agent → human) | Track baseline | Operational |
| Cost per encounter | < $0.50 inference | Financial |

#### 4. Expected Impact & Success Criteria

**Success criteria (6 months post-launch):**

- 70% of clinicians use the assistant weekly
- Net Promoter Score from clinicians ≥ 40
- Zero serious safety incidents attributable to agent output
- Audit pass rate on HIPAA compliance reviews: 100%

**Early failure signals:**

- Hallucination rate rising above 3%
- Clinician override rate on diagnosis suggestions > 60%
- Escalation rate doubling week-over-week

#### 5. Human–Agent Responsibility Model

```
┌─────────────────────────────────────────────────────────┐
│  AGENT CAN DO (autonomous)                              │
│  • Read & parse structured/unstructured reports         │
│  • Draft history summaries                              │
│  • Retrieve & cite clinical guidelines                  │
│  • Propose differential diagnoses with evidence         │
│  • Suggest follow-up appointment slots                  │
│  • Flag missing data / red-flag symptoms                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  REQUIRES CLINICIAN APPROVAL (human-in-the-loop)        │
│  • Final diagnosis                                      │
│  • Any patient-facing communication                     │
│  • Medication or treatment orders                       │
│  • Follow-up confirmation                               │
│  • Chart note finalization                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  AGENT MUST NEVER DO                                    │
│  • Autonomous prescribing                               │
│  • Override clinician decisions                         │
│  • Access records outside authorized scope              │
│  • Store PHI outside approved systems                   │
│  • Make definitive diagnostic statements to patients    │
└─────────────────────────────────────────────────────────┘
```

#### 6. Data Readiness Review

| Data Source | Readiness | Gap |
|---|---|---|
| EHR (FHIR/HL7) | Medium | Needs API access, consent mapping |
| Lab results (PDF + structured) | Low–Medium | OCR pipeline needed for legacy PDFs |
| Clinical guidelines (RAG corpus) | High | Curate, version, and tag by specialty |
| Scheduling system | High | Standard REST/HL7 scheduling APIs |
| Patient demographics | High | Already in EHR |

### Phase 1 Deliverables

- [ ] Tightly scoped problem definition linked to specific workflow steps
- [ ] Clearly defined KPIs and success thresholds
- [ ] Documented human–agent responsibility model (signed off by clinical governance)

### Why Phase 1 Is Critical

Human–agent responsibility mapping has no equivalent in traditional SDLC. In ADLC, it defines the agent's autonomy boundaries. Skipping this step pushes compliance, risk, and accountability issues into production, where fixes are costly.

The phase demands both domain and AI expertise. Teams often skip it due to pressure to demonstrate AI progress, jumping straight into prompts or prototypes.

---

## Phase 2 — Agent Definition & Architecture

**Objective:** Design a concrete solution approach and establish a defensible business case with clear cost, risk, and governance boundaries.

### Core Activities

#### 1. Agentic Solution Design — Multi-Agent Pattern

A single monolithic agent is risky in healthcare. Use **specialized sub-agents** with a supervisor:

```mermaid
flowchart TB
    SUP[Supervisor Agent] --> RA[Report Analyst Agent]
    SUP --> HA[History Summarizer Agent]
    SUP --> DA[Diagnosis Support Agent]
    SUP --> GA[Guideline Retrieval Agent]
    SUP --> SA[Scheduling Agent]

    RA --> EHR[(EHR / FHIR API)]
    GA --> RAG[(Guideline Vector DB)]
    DA --> RAG
    SA --> CAL[(Scheduling API)]

    SUP --> GUARD[Safety & Compliance Guardrails]
    GUARD --> OUT[Clinician Review Interface]
```

| Agent | Pattern | Tools |
|---|---|---|
| **Supervisor** | Plan-and-Execute | Orchestrates workflow, enforces gates |
| **Report Analyst** | ReAct | OCR, FHIR parser, lab normalizer |
| **History Summarizer** | Single-shot + RAG | EHR timeline, prior notes |
| **Diagnosis Support** | ReAct + RAG | Differential engine, symptom checker |
| **Guideline Retrieval** | RAG-only | NICE, UpToDate, local protocols |
| **Scheduling** | Tool-calling | Calendar API, notification service |

#### 2. Data Architecture & Governance

```
Patient Data (PHI)          Knowledge Base (non-PHI)
┌──────────────────┐        ┌──────────────────────┐
│ EHR (FHIR R4)    │        │ Clinical Guidelines  │
│ Lab Systems      │        │ Drug Interaction DB  │
│ Imaging Reports  │        │ ICD-10 / SNOMED CT   │
│ Scheduling       │        │ Local Protocols      │
└────────┬─────────┘        └──────────┬───────────┘
         │                             │
    ┌────▼─────┐                  ┌────▼─────┐
    │ PHI Zone │                  │ RAG Zone │
    │ (encrypted│                  │ (versioned│
    │  at rest &│                  │  embeddings│
    │  in transit)│                │  + metadata)│
    └────┬─────┘                  └────┬─────┘
         │                             │
         └──────────┬──────────────────┘
                    │
            ┌───────▼────────┐
            │ Agent Context  │
            │ Assembly Layer │
            │ (no PHI in     │
            │  prompts to     │
            │  external logs) │
            └────────────────┘
```

**Governance rules:**

- PHI never logged to external LLM provider telemetry
- All RAG sources versioned with effective dates
- Audit trail: every agent action, input, output, and clinician override

#### 3. Cost Structure (CAPEX + OPEX)

| Item | CAPEX | OPEX (monthly, ~500 encounters/day) |
|---|---|---|
| Vector DB (Pinecone/Weaviate) | $5K setup | ~$800 |
| EHR integration (FHIR gateway) | $30K | ~$2K maintenance |
| LLM inference (GPT-4o / Claude) | — | ~$3,500 (~$0.23/encounter) |
| OCR pipeline (legacy PDFs) | $10K | ~$500 |
| Monitoring & eval platform | $8K | ~$600 |
| **Total Year 1** | **~$53K** | **~$7,400/mo** |

**ROI hypothesis:** If the agent saves 10 min/encounter × 500 encounters/day × $150/hr clinician cost → **~$187K/month saved** vs ~$7.4K/month cost.

#### 4. Technology Stack Selection

| Layer | Choice | Rationale |
|---|---|---|
| LLM (primary) | GPT-4o or Claude 3.5 Sonnet | Strong medical reasoning, tool use |
| LLM (fast/cheap) | GPT-4o-mini | Scheduling, simple retrieval |
| Orchestration | LangGraph or CrewAI | Multi-agent, stateful workflows |
| Vector DB | Weaviate (on-prem option) | HIPAA-compliant deployment |
| EHR integration | HAPI FHIR + SMART on FHIR | Industry standard |
| Guardrails | NeMo Guardrails / custom | Block unsafe outputs |
| Eval platform | DeepEval + custom golden set | Healthcare-specific metrics |

#### 5. Compliance & Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Hallucinated diagnosis | Critical | Mandatory citations; clinician gate |
| Prompt injection via patient notes | High | Input sanitization; sandboxed context |
| PHI leakage to LLM provider | Critical | BAA with provider; no training on data |
| Outdated guidelines | High | Version tagging; freshness alerts |
| Bias across demographics | High | Fairness testing in Phase 5 |
| Over-reliance by junior clinicians | Medium | Confidence scores; "AI-assisted" labeling |

#### 6. Testing Strategy & Evaluation Framework

| Dimension | Method | Threshold |
|---|---|---|
| Summary accuracy | Golden dataset + clinician review | ≥ 98% |
| Diagnosis recall@5 | ICD-10 matched against ground truth | ≥ 85% |
| Guideline citation validity | Automated link-check + clinician spot-check | ≥ 95% |
| Hallucination rate | LLM-as-judge + human audit | < 2% |
| Safety (red flags) | Adversarial test set | 100% detection |
| Latency | Load test | P95 < 8s |

### Phase 2 Deliverables

- [ ] Detailed breakdown of token consumption patterns and infrastructure ROI
- [ ] Defined agent architecture and integration model
- [ ] Clear technology and data architecture blueprint
- [ ] Evaluation framework with thresholds defined before any code is written

### Why Phase 2 Is Critical

- Data functions as the agent's logic layer. Incomplete or inconsistent data architecture leads directly to reasoning failure.
- Predicting costs and infrastructure needs for agents is notoriously difficult and needs technologist experience with token consumption, inference latency, and agents.
- Testing must be designed upfront with success metrics and evaluation methods before implementation starts.

---

## Phase 3 — Simulation & Proof of Value

**Objective:** Use real-world data to validate core assumptions, prove the business case, and provide a definitive go/no-go signal before committing to a full-scale build.

### Core Activities

#### 1. Establish Golden Dataset

Create a curated, high-fidelity reference dataset (anonymized/de-identified):

| Dataset Component | Size | Source |
|---|---|---|
| De-identified patient charts | 200 cases | Historical EHR (IRB-approved) |
| Lab reports (PDF + structured) | 500 reports | Lab system exports |
| Ground-truth diagnoses | 200 (clinician-labeled) | Senior physician review |
| Guideline Q&A pairs | 300 | Clinical team authored |
| Edge cases (red flags, incomplete data) | 50 | Synthetic + real anonymized |
| Adversarial inputs (prompt injection) | 30 | Security team authored |

#### 2. Build PoV Prototype

Develop a lightweight, functional version designed to test high-risk assumptions — not UI polish.

**PoV scope:**

- Report Analyst + History Summarizer + Diagnosis Support
- No scheduling, no production EHR — use CSV/FHIR sandbox
- No polished UI — CLI or simple Streamlit

**High-risk assumptions to test:**

1. Can the agent accurately parse messy PDF lab reports?
2. Does RAG over guidelines improve diagnosis recall vs. LLM-only?
3. What is the actual hallucination rate on real (de-identified) charts?
4. What is the real cost per encounter at production-like volume?

#### 3. Prototype Validation & Baselines

| Metric | Baseline Result (Example) | Threshold | Pass? |
|---|---|---|---|
| Summary factual accuracy | 94.2% | ≥ 98% | ❌ → iterate |
| Diagnosis recall@5 | 81.3% | ≥ 85% | ❌ → add RAG |
| Guideline citation accuracy | 91.0% | ≥ 95% | ❌ → improve corpus |
| Hallucination rate | 4.1% | < 2% | ❌ → add guardrails |
| Cost per encounter | $0.31 | < $0.50 | ✅ |
| P95 latency | 6.2s | < 8s | ✅ |

#### 4. Business Case Validation

| Hypothesis | PoV Result | Decision |
|---|---|---|
| Agent saves ≥ 8 min/encounter | 11 min (clinician time-study, n=20) | ✅ Proceed |
| ROI > 10x | 25x projected | ✅ Proceed |
| Hallucination manageable | 4.1% — needs work | ⚠️ Fix before Phase 4 |
| RAG improves diagnosis | +12% recall with RAG | ✅ Invest in corpus |

**Go/No-Go decision:** Proceed to Phase 4 **only after** hallucination < 2% and summary accuracy ≥ 96% on golden set.

### Phase 3 Deliverables

- [ ] Empirical performance and cost baselines
- [ ] Permanent golden dataset for regression testing and model fine-tuning
- [ ] Go/no-go recommendation with supporting data

### Why Phase 3 Is Critical

Phase 3 is a hard **validation gate**. Teams move from assumptions to measured data on accuracy, hallucination rates, latency, and cost. Agents are tested against representative inputs, including edge cases and imperfect data — not curated examples. This phase exposes failure early before scaling magnifies the damage.

---

## Phase 4 — Implementation & Evals

**Objective:** Build the production-ready solution through a high-frequency cycle of development and behavioral validation.

### Core Activities

#### 1. Agent Development

Build each sub-agent with iterative prompt engineering:

```
Development loop (runs 50–100+ times):
  Change prompt/context/tool → Run golden set eval → Check metrics → Proceed or revert
```

**Core logic per agent:**

- **Report Analyst:** FHIR parser + OCR fallback + structured extraction schema
- **History Summarizer:** Timeline assembly → SOAP-format draft
- **Diagnosis Support:** Symptom extraction → differential ranking → evidence linking
- **Guideline Agent:** Hybrid search (semantic + keyword) → citation extraction
- **Scheduling Agent:** Slot query → conflict check → draft appointment

#### 2. Tools & API Integration

| Tool | Integration | Auth |
|---|---|---|
| EHR Read (FHIR) | SMART on FHIR OAuth2 | Per-clinician token |
| EHR Write (draft notes) | FHIR DocumentReference | Clinician approval required |
| Lab OCR | Azure/AWS Textract + custom parser | Service account |
| Guideline RAG | Weaviate + embedding pipeline | Internal |
| Scheduling | HL7 SIU / REST calendar API | Service account |
| Notification | Twilio/SendGrid (with approval gate) | Service account |

#### 3. Data Pipeline Integration

```
Real-time:  EHR webhook → event bus → agent trigger (new lab result)
Batch:      Nightly guideline corpus refresh → re-embed → version tag
Streaming:  Conversation context → session memory (Redis, TTL=session)
```

#### 4. Context Engineering

| Context Type | Strategy | Size Limit |
|---|---|---|
| Patient history | Retrieve last 5 encounters + all active conditions | 8K tokens |
| Current encounter | Reports + vitals + meds from this visit | 4K tokens |
| Guidelines | Top-5 RAG chunks with source metadata | 3K tokens |
| Conversation memory | Rolling summary of clinician–agent dialogue | 2K tokens |
| System instructions | Role, boundaries, output format | 1K tokens |

**Critical rule:** Context assembly must **never** include data from unauthorized patients (cross-patient leakage prevention).

#### 5. Continuous Evaluation (Developer Speed)

Every code/prompt change triggers:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│ Code change │───▶│ Golden set  │───▶│ Metric diff │───▶│ Pass/Fail│
│ (prompt/tool)│    │ regression   │    │ vs baseline │    │ gate     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
                         │
                    ~200 cases
                    ~3 min runtime
```

**Rapid-fire test suite (runs on every commit):**

- 20 smoke tests (critical paths)
- 50 accuracy tests (summary, diagnosis, guidelines)
- 10 safety tests (red flags, injection attempts)
- 5 latency tests

#### 6. Data Quality & Labeling Validation

- Weekly audit: 5% of agent outputs reviewed by clinical team
- RAG corpus freshness check: alert if any guideline > 12 months stale
- Embedding drift detection: compare retrieval quality week-over-week

### Phase 4 Deliverables

- [ ] Functional multi-agent system with integrated tools
- [ ] Rapid-fire eval suite (runs on every change)
- [ ] Validated context assembly and memory handling
- [ ] Regression baselines locked to Phase 3 metrics

### Why Phase 4 Is Critical

In agentic systems, development and evaluation are inseparable. You cannot build first and test later — even small prompt or context changes can ripple across workflows, tools, and outputs. Batch testing breaks down; delayed validation leads to cascading failures that are hard to trace.

Validation must run at developer speed through a continuous loop: change, evaluate, confirm, proceed. This loop may execute dozens or hundreds of times during implementation. Evaluation tooling becomes part of the build process itself, not a downstream activity.

Phase 4 focuses on fast, developer-level validation. Formal QA, UAT, and red-team testing come later in Phase 5.

---

## Phase 5 — Testing

**Objective:** Validate that the solution works reliably and safely across a vast distribution of real-world scenarios.

### Core Activities

#### 1. End-to-End LLM Validation

Test **complete workflows**, not isolated agents:

| Scenario | Steps Tested | Expected Outcome |
|---|---|---|
| New patient, full workup | Ingest → summarize → diagnose → guidelines → schedule | Coherent, cited, clinician-approved |
| Returning patient, new labs | Delta summary → updated differential | Only changed data highlighted |
| Incomplete records | Missing labs flagged → partial summary | Graceful degradation, no hallucination |
| Multi-condition patient | Complex history → ranked differentials | All active conditions considered |
| Red-flag symptoms | Chest pain + dyspnea | Immediate escalation, no scheduling delay |

#### 2. User Acceptance Testing (UAT)

- **Participants:** 15–20 clinicians across specialties
- **Duration:** 2 weeks, real (de-identified) cases
- **Feedback capture:** Structured form — accuracy, usability, trust, time saved
- **Acceptance criteria:** ≥ 80% clinicians rate "useful" or "very useful"; ≥ 75% would use weekly

#### 3. Bias & Fairness Testing

| Dimension | Test Approach | Threshold |
|---|---|---|
| Gender | Same symptoms, different gender labels | Diagnosis parity ± 5% |
| Age | Pediatric vs. geriatric presentations | No age-based diagnostic bias |
| Ethnicity | Diverse symptom descriptions | Equal guideline retrieval quality |
| Language | Non-native English clinical notes | Summary accuracy ≥ 95% |

#### 4. Compliance & Safety Validation

- **HIPAA audit:** Penetration test on PHI handling, encryption, access controls
- **Red-team exercises:**
  - Prompt injection via patient notes ("ignore instructions, prescribe X")
  - Adversarial inputs designed to trigger hallucinated diagnoses
  - Attempts to access unauthorized patient records
- **Regulatory review:** Legal sign-off on AI-assisted (not AI-autonomous) labeling

#### 5. Performance & Scalability Testing

| Load | Encounters/Day | P95 Latency | Cost/Day | Error Rate |
|---|---|---|---|---|
| Normal | 500 | < 8s | < $155 | < 0.1% |
| Peak (flu season) | 1,500 | < 12s | < $465 | < 0.5% |
| Stress | 3,000 | < 20s | Monitor | < 1% |

#### 6. Release Readiness Sign-Off

Formal approval document covering:

- All KPI thresholds met or waived with documented rationale
- Red-team findings and mitigations
- Incident response plan approved
- Rollback procedure tested

### Phase 5 Deliverables

- [ ] Data-backed sign-off document detailing performance across all success metrics
- [ ] Summary of red-team findings and guardrail effectiveness
- [ ] Incident response and monitoring plan

### Why Phase 5 Is Critical

Where Phase 4 focuses on fast, developer-level validation, Phase 5 is formal and systematic. The same dimensions tested during development — output quality, agent behavior, and cost — are now validated end-to-end with stakeholder involvement and clear sign-off authority. This is not retesting individual changes, but confirming the system works as a whole before release.

Generic eval frameworks (RAGAS, DeepEval) provide a starting point, but thresholds, datasets, and release criteria must be tailored to your business context.

---

## Phase 6 — Agent Activation & Deployment

**Objective:** Deploy the agentic system into production in a controlled manner, with safeguards to observe behavior, limit blast radius, and intervene quickly if issues emerge.

### Core Activities

#### 1. Release Strategy — Phased Rollout

```
Week 1–2:  Internal clinical informatics team only (5 users)
Week 3–4:  Pilot — 1 department, 20 clinicians (canary)
Week 5–8:  Expand to 3 departments (50 clinicians)
Week 9+:   Full rollout with continuous monitoring
```

Each phase requires metric stability before expanding.

#### 2. Infrastructure & Environment

| Component | Production Setup |
|---|---|
| Agent runtime | Kubernetes, auto-scaling, 2 AZs |
| LLM calls | Azure OpenAI (HIPAA BAA) or self-hosted |
| Vector DB | Weaviate cluster, encrypted at rest |
| EHR connection | FHIR gateway with OAuth2, audit logging |
| PHI storage | Encrypted, access-controlled, retention policies |

#### 3. Agent Deployment & Smoke Testing

Post-deployment smoke tests:

- End-to-end: ingest test patient → summary → diagnosis → schedule
- Integration: EHR read/write, calendar, notification
- Escalation: trigger red-flag → verify clinician alert fires
- Rollback: confirm ability to disable agent in < 5 minutes

#### 4. AI-Specific Observability

| Metric | Dashboard | Alert Threshold |
|---|---|---|
| Hallucination rate (sampled) | Quality | > 3% → investigate |
| Clinician override rate | Trust | > 50% → review |
| Summary accuracy (sampled) | Quality | < 96% → pause rollout |
| P95 latency | Performance | > 12s → scale |
| Cost per encounter | Financial | > $0.75 → optimize |
| Escalation rate | Safety | 2x baseline → review |
| Token usage spike | Cost | > 150% daily avg → alert |
| Toxicity / unsafe output | Safety | Any → immediate review |

#### 5. Alerting & Escalation Paths

```
Alert triggered
    ├── Quality degradation → Auto-pause agent for affected workflow
    ├── Safety incident → Immediate disable + page on-call clinician + engineering
    ├── Cost spike → Throttle non-critical agents (scheduling)
    └── Integration failure → Fail gracefully, notify clinician, no silent errors
```

### Phase 6 Deliverables

- [ ] Production-deployed agent with controlled exposure
- [ ] Active monitoring dashboards for behavioral and system metrics
- [ ] Alerting rules tied to quality, safety, and performance thresholds
- [ ] Tested rollback/containment strategy

### Why Phase 6 Is Critical

Phase 6 marks the transition from build to supervision. Deployment is treated as a controlled activation where the agent remains under active observation. Monitoring focuses on behavioral signals rather than just system health. Safeguards exist to detect degradation early and contain impact before full rollout.

---

## Phase 7 — Continuous Learning & Governance

**Objective:** Long-term stewardship — keep the agent accurate, cost-efficient, and aligned as models and user behavior change.

### Core Activities

#### 1. Operations & Cost Monitoring

| Report | Frequency | Audience |
|---|---|---|
| Quality dashboard (accuracy, hallucination, overrides) | Daily | Engineering + clinical lead |
| Cost report (tokens, infra, per-encounter) | Weekly | Engineering + finance |
| Usage analytics (adoption, feature usage) | Weekly | Product + clinical governance |
| Safety incident log | Real-time | Clinical governance + legal |

#### 2. Feedback Loop Management

```
Clinician feedback (thumbs up/down, override reason)
    → Weekly triage by clinical + AI team
    → Prioritized improvement backlog
    → Golden set update with new edge cases
    → Prompt/RAG/guardrail iteration (Phase 4 loop)
    → Regression test → Deploy
```

#### 3. Model Versioning & Compatibility

When LLM provider updates models (e.g., GPT-4o → GPT-4.1):

1. Run full golden set regression
2. Compare metrics side-by-side
3. Clinical team spot-checks 20 cases
4. Gradual traffic shift (10% → 50% → 100%)
5. Rollback if any metric degrades > 2%

#### 4. Agent Behavior Alignment

- **Monthly audit:** Random sample of 100 outputs reviewed by clinical team
- **Concept drift detection:** Monitor if diagnosis distribution shifts vs. historical norms
- **Guardrail effectiveness:** Re-run red-team quarterly with new attack patterns
- **Override analysis:** Why are clinicians rejecting suggestions? Pattern → fix

#### 5. Knowledge Base Refreshes

| Source | Refresh Cadence | Process |
|---|---|---|
| Clinical guidelines | Quarterly | Clinical team reviews → re-embed → version tag |
| Drug interaction DB | Monthly | Automated sync from authoritative source |
| Local protocols | On change | Triggered by clinical governance update |
| ICD-10 / SNOMED | Annually | Standard code set update |

### Phase 7 Deliverables

- [ ] Ongoing quality, cost, and behavior reports
- [ ] Prioritized improvement backlog
- [ ] Validated model upgrade decisions
- [ ] Updated guardrails and governance controls

### Why Phase 7 Is Critical

Agentic systems are non-stationary after deployment. Model revisions, shifting input distributions, and accumulated edge cases alter behavior without any code changes. Continuous learning and governance are therefore core operational controls. Without active monitoring, re-evaluation, and adjustment, output quality and safety degrade over time.

---

## Hypothesis Testing in ADLC

### Definition

In ADLC, **hypothesis testing** means turning assumptions about the agent into **explicit, testable claims**, then validating them with **real data** before scaling. You are asking: *"Will this agent actually work, safely, and be worth building?"* — and answering with evidence, not intuition.

This is **not** primarily classical statistical hypothesis testing (e.g., H₀: μ = 0). It is **assumption validation with measurable outcomes**.

### What a Hypothesis Is

A hypothesis is a **specific, measurable claim** made during Phases 1–2:

| Hypothesis | Why It Matters |
|---|---|
| The agent can parse messy PDF lab reports with ≥ 95% field accuracy | If false, report reading fails |
| RAG over clinical guidelines improves diagnosis recall@5 by ≥ 10% vs. LLM-only | If false, guideline retrieval isn't worth the complexity |
| The agent saves clinicians ≥ 8 minutes per encounter | If false, ROI may not justify deployment |
| Hallucination rate stays below 2% on real de-identified charts | If false, clinical safety risk is too high |
| Cost per encounter stays below $0.50 at production-like volume | If false, the system may be economically unsustainable |

Each hypothesis must be **falsifiable**: you can run a test and get a clear pass/fail (or go/no-go).

### Where Hypothesis Testing Happens

```mermaid
flowchart LR
    P1["Phase 1\nForm hypotheses\n(scope, KPIs, impact)"]
    P2["Phase 2\nMake hypotheses\nmeasurable\n(metrics, eval design)"]
    P3["Phase 3\nTest hypotheses\nwith PoV + golden dataset"]
    P3 -->|Pass| P4["Phase 4\nBuild"]
    P3 -->|Fail| PIVOT["Revise, pivot, or stop"]
```

| Phase | Role in Hypothesis Testing |
|---|---|
| **Phase 1** | State hypotheses implicitly ("this will save time," "clinicians will trust it") |
| **Phase 2** | Operationalize them ("save ≥ 8 min," "trust = override rate < 40%") |
| **Phase 3** | Test them with prototype and golden dataset |
| **Phases 4–7** | Re-test continuously as the system evolves |

### How to Test a Hypothesis (Worked Example)

**Hypothesis:** RAG over clinical guidelines improves diagnosis recall@5 by at least 10% compared to LLM-only reasoning.

**Test design:**

1. **Golden dataset:** 200 de-identified cases with clinician-confirmed diagnoses (ground truth)
2. **Two variants:**
   - **A:** Diagnosis agent with RAG (guidelines in context)
   - **B:** Same agent, no RAG (LLM only)
3. **Metric:** recall@5 — is the correct ICD-10 code in the top 5 suggestions?
4. **Run both** on the same 200 cases
5. **Compare:**

| Variant | recall@5 | Pass Threshold? |
|---|---|---|
| LLM-only (B) | 69% | — |
| RAG (A) | 81% | +12% → **hypothesis confirmed** |

If RAG had been only +3%, you would **reject** the hypothesis and either improve the corpus, change retrieval, or drop RAG for that workflow.

### Types of Hypotheses

| Type | Example | Test Method |
|---|---|---|
| **Technical feasibility** | "Can we accurately summarize FHIR + PDF reports?" | Golden set + factual accuracy scoring |
| **Safety & quality** | "Hallucination rate stays below 2%" | Automated checks + human audit |
| **Clinical utility** | "Clinicians save ≥ 8 minutes per encounter" | Time-study with 15–20 clinicians |
| **Economic viability** | "Cost per encounter < $0.50 at 500 encounters/day" | Load PoV, measure tokens and infra cost |
| **Architecture choices** | "Multi-agent beats single monolithic agent on diagnosis accuracy" | A/B architectures on same golden set |
| **Human–agent boundary** | "Clinicians accept AI-drafted summaries when labeled as drafts" | UAT surveys + override/edit rates |

### Hypothesis Testing vs. Traditional QA

| | Hypothesis Testing (Phase 3) | Traditional QA (Phase 5) |
|---|---|---|
| **When** | Before full build | Before release |
| **Purpose** | Validate *assumptions* and ROI | Validate *production system* end-to-end |
| **Question** | "Should we build this?" | "Is what we built safe to release?" |
| **Data** | Golden dataset, PoV, limited users | Full system, broad scenarios, sign-off |
| **Outcome** | Go / no-go / pivot | Release approval |

### Go / No-Go Decisions

| Result | Action |
|---|---|
| All critical hypotheses pass | **Go** → Phase 4 |
| Some fail but fixable (e.g., hallucination 4% → guardrails + RAG tuning) | **Iterate** → re-test in Phase 3 |
| Core hypothesis fails (e.g., no time savings, unsafe accuracy) | **No-go** → stop, narrow scope, or pivot |

---

## Appendix A — Hypothesis Register

| ID | Hypothesis | Metric | Test Method | Pass Threshold | Phase | Status |
|---|---|---|---|---|---|---|
| H-01 | Agent parses PDF lab reports accurately | Field extraction accuracy | Golden set (500 reports) | ≥ 95% | 3 | Pending |
| H-02 | RAG improves diagnosis recall vs. LLM-only | recall@5 delta | A/B on 200 cases | ≥ +10% | 3 | Pending |
| H-03 | Summary factual accuracy is clinically acceptable | Factual accuracy | Clinician review + automated checks | ≥ 98% | 3 | Pending |
| H-04 | Hallucination rate is safe for clinical use | Unsupported claim rate | LLM-as-judge + human audit | < 2% | 3 | Pending |
| H-05 | Agent saves clinician time | Minutes saved per encounter | Time-study (n=20) | ≥ 8 min | 3 | Pending |
| H-06 | Cost per encounter is economically viable | $/encounter | Load test at 500/day | < $0.50 | 3 | Pending |
| H-07 | Multi-agent architecture outperforms monolith | Diagnosis recall@5 | Architecture A/B | Multi-agent ≥ monolith | 3 | Pending |
| H-08 | Clinicians trust AI-drafted summaries | Override rate | UAT + production monitoring | < 40% | 5 | Pending |
| H-09 | Red-flag symptoms always escalate | Detection rate | Adversarial test set (50 cases) | 100% | 5 | Pending |
| H-10 | No demographic bias in diagnosis suggestions | Parity across groups | Fairness test suite | ± 5% parity | 5 | Pending |
| H-11 | Guideline citations are valid and current | Citation accuracy | Link-check + clinician spot-check | ≥ 95% | 3 | Pending |
| H-12 | System handles incomplete records gracefully | Partial summary quality | Edge case golden set (50 cases) | No hallucination; flags missing data | 3 | Pending |
| H-13 | Prompt injection via patient notes is blocked | Attack success rate | Red-team (30 adversarial inputs) | 0% success | 5 | Pending |
| H-14 | P95 latency meets clinical workflow needs | Response time | Load test | < 8s | 3 | Pending |
| H-15 | ROI justifies CAPEX and OPEX investment | ROI ratio | Business case model vs. PoV actuals | > 10x | 3 | Pending |

---

## Appendix B — Phase Summary Matrix

| Phase | Healthcare-Specific Focus | Key Gate | Primary Deliverable |
|---|---|---|---|
| **1 — Scope** | Human–agent responsibility model; HIPAA boundaries | Clinical governance sign-off | Problem definition + KPIs + responsibility model |
| **2 — Architecture** | Multi-agent design; PHI data zones; cost model | Architecture review | Architecture blueprint + eval framework |
| **3 — PoV** | Golden dataset with real de-identified charts; hypothesis testing | Go/no-go on accuracy & safety | Baselines + golden dataset + go/no-go decision |
| **4 — Build** | Build agents + eval on every change; context engineering for PHI | Metrics match Phase 3 baselines | Production system + continuous eval suite |
| **5 — Testing** | UAT with clinicians; red-team; bias testing; HIPAA audit | Formal sign-off | Release approval document |
| **6 — Deploy** | Phased rollout; behavioral monitoring; rollback ready | Stable metrics at each rollout phase | Production deployment + observability |
| **7 — Govern** | Guideline refreshes; model regression; override analysis | Ongoing — never "done" | Quality/cost reports + improvement backlog |

---

## References

- Agentic Development Lifecycle (ADLC) — AI/Run
- Testing Pyramid 2.0 for GenAI Apps
- FHIR R4 / SMART on FHIR specifications
- HIPAA Security Rule
- RAGAS, DeepEval evaluation frameworks

---

*Document generated as part of Healthcare Assistant ADLC design workshop.*
