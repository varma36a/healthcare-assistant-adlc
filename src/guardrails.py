"""Safety guardrails for the healthcare agent."""

from src.config import PROMPT_INJECTION_PATTERNS, UNSAFE_ACTIONS


def detect_prompt_injection(text: str) -> list[str]:
    lower = text.lower()
    return [p for p in PROMPT_INJECTION_PATTERNS if p in lower]


def sanitize_clinical_notes(notes: str) -> tuple[str, list[str]]:
    """Strip injection patterns from notes; return cleaned text + warnings."""
    warnings = detect_prompt_injection(notes)
    cleaned = notes
    for pattern in PROMPT_INJECTION_PATTERNS:
        idx = cleaned.lower().find(pattern)
        while idx != -1:
            end = idx + len(pattern)
            cleaned = cleaned[:idx] + "[REDACTED-INJECTION]" + cleaned[end:]
            idx = cleaned.lower().find(pattern)
    return cleaned, warnings


def block_unsafe_action(action: str) -> bool:
    return any(unsafe in action.lower() for unsafe in UNSAFE_ACTIONS)


def check_red_flag(patient: dict) -> bool:
    if patient.get("red_flag"):
        return True
    notes = patient.get("notes", "").lower()
    red_flag_symptoms = ["chest pain", "shortness of breath", "confusion", "fever"]
    return any(s in notes for s in red_flag_symptoms) and patient.get("red_flag", False) is not False
