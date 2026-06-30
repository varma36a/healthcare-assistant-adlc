"""Healthcare Assistant MCP Server — exposes tools via Model Context Protocol."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from src.tools.ehr_tool import list_patients, parse_lab_report, read_patient
from src.tools.guideline_tool import search_clinical_guidelines
from src.tools.schedule_tool import book_appointment, get_available_slots, propose_appointment
from src.agents.supervisor import SupervisorAgent

server = Server("healthcare-assistant")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_patient_record",
            description="Read a dummy patient record from the EHR by patient ID (e.g. P-001). Sanitizes prompt injection in notes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "Patient ID, e.g. P-001"},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="parse_lab_report",
            description="Parse and extract structured findings from a patient's lab report.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="search_clinical_guidelines",
            description="RAG search over clinical guidelines vector store. Returns top matching guidelines with citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Clinical query, e.g. 'type 2 diabetes management HbA1c 8.2'"},
                    "top_k": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_available_slots",
            description="Get available appointment slots from the scheduling system.",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialty": {"type": "string", "description": "Optional specialty filter"},
                    "limit": {"type": "integer", "default": 3},
                },
            },
        ),
        Tool(
            name="propose_appointment",
            description="Propose a follow-up appointment. Requires clinician approval to confirm.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "reason": {"type": "string"},
                    "specialty": {"type": "string"},
                },
                "required": ["patient_id", "reason"],
            },
        ),
        Tool(
            name="book_appointment",
            description="Book an appointment. BLOCKED unless clinician_approved=true.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string"},
                    "slot_id": {"type": "string"},
                    "clinician_approved": {"type": "boolean", "default": False},
                },
                "required": ["patient_id", "slot_id"],
            },
        ),
        Tool(
            name="run_clinical_workflow",
            description="Run the full multi-agent clinical workflow: read reports → summarize → diagnose → guidelines (RAG) → schedule.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "string", "description": "Patient ID, e.g. P-001"},
                },
                "required": ["patient_id"],
            },
        ),
        Tool(
            name="list_patients",
            description="List all dummy patients in the dataset.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "read_patient_record":
            result = read_patient(arguments["patient_id"])
        elif name == "parse_lab_report":
            patient = read_patient(arguments["patient_id"])
            result = parse_lab_report(patient)
        elif name == "search_clinical_guidelines":
            result = search_clinical_guidelines(arguments["query"], arguments.get("top_k", 3))
        elif name == "get_available_slots":
            result = get_available_slots(arguments.get("specialty"), arguments.get("limit", 3))
        elif name == "propose_appointment":
            result = propose_appointment(
                arguments["patient_id"],
                arguments["reason"],
                arguments.get("specialty"),
            )
        elif name == "book_appointment":
            result = book_appointment(
                arguments["patient_id"],
                arguments["slot_id"],
                arguments.get("clinician_approved", False),
            )
        elif name == "run_clinical_workflow":
            supervisor = SupervisorAgent()
            wf = supervisor.run(arguments["patient_id"])
            result = {
                "patient_id": wf.patient_id,
                "red_flag": wf.red_flag,
                "escalations": wf.escalations,
                "summary": wf.summary,
                "diagnosis": wf.diagnosis,
                "guidelines": wf.guidelines,
                "scheduling": wf.scheduling,
                "latency_sec": wf.latency_sec,
                "audit_log": wf.audit_log,
            }
        elif name == "list_patients":
            patients = list_patients()
            result = [{"patient_id": p["patient_id"], "name": p["name"], "diagnosis": p.get("ground_truth_diagnosis_label")} for p in patients]
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
