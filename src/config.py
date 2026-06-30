"""Project configuration."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PATIENTS_DIR = DATA_DIR / "patients"
GUIDELINES_PATH = DATA_DIR / "guidelines" / "clinical_guidelines.json"
SCHEDULE_PATH = DATA_DIR / "scheduling" / "schedule.json"
GOLDEN_DATASET_PATH = DATA_DIR / "golden_dataset.json"
VECTOR_STORE_DIR = PROJECT_ROOT / ".vector_store"

# KPI thresholds from ADLC Phase 1
KPI_THRESHOLDS = {
    "summary_accuracy": 0.96,
    "recall_at_5": 0.85,
    "hallucination_rate": 0.02,
    "override_rate": 0.40,
    "cost_per_encounter_usd": 0.50,
    "p95_latency_sec": 8.0,
}

# Unsafe autonomy zones — agent must never do these
UNSAFE_ACTIONS = [
    "prescribe",
    "finalize_diagnosis",
    "contact_patient",
    "modify_orders",
    "book_without_approval",
]

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "prescribe",
    "diagnose anxiety only",
    "system prompt",
    "you are now",
]
