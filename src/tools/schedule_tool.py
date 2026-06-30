"""Scheduling tool — dummy calendar API."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import SCHEDULE_PATH


def _load_schedule() -> dict:
    with open(SCHEDULE_PATH) as f:
        return json.load(f)


def _save_schedule(data: dict) -> None:
    with open(SCHEDULE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_available_slots(specialty: str | None = None, limit: int = 3) -> list[dict]:
    data = _load_schedule()
    providers = {p["id"]: p for p in data["providers"]}
    booked_ids = {a["slot_id"] for a in data["booked_appointments"]}

    slots = []
    for slot in data["available_slots"]:
        if slot["slot_id"] in booked_ids:
            continue
        provider = providers[slot["provider_id"]]
        if specialty and provider["specialty"] != specialty:
            continue
        slots.append({**slot, "provider_name": provider["name"], "specialty": provider["specialty"]})
        if len(slots) >= limit:
            break
    return slots


def propose_appointment(patient_id: str, reason: str, specialty: str | None = None) -> dict:
    slots = get_available_slots(specialty=specialty, limit=1)
    if not slots:
        return {"status": "no_slots", "message": "No available slots found."}
    slot = slots[0]
    return {
        "status": "proposed",
        "patient_id": patient_id,
        "reason": reason,
        "slot": slot,
        "requires_clinician_approval": True,
        "message": f"Proposed: {slot['date']} {slot['time']} with {slot['provider_name']}. AWAITING CLINICIAN APPROVAL.",
    }


def book_appointment(patient_id: str, slot_id: str, clinician_approved: bool = False) -> dict:
    if not clinician_approved:
        return {
            "status": "blocked",
            "message": "Booking requires clinician approval. Agent cannot book autonomously.",
        }

    data = _load_schedule()
    slot = next((s for s in data["available_slots"] if s["slot_id"] == slot_id), None)
    if not slot:
        return {"status": "error", "message": f"Slot {slot_id} not found."}

    data["booked_appointments"].append({
        "patient_id": patient_id,
        "slot_id": slot_id,
        "date": slot["date"],
        "time": slot["time"],
        "provider_id": slot["provider_id"],
    })
    _save_schedule(data)
    return {"status": "confirmed", "slot_id": slot_id, "patient_id": patient_id}
