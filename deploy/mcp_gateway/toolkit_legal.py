"""
B-SDD MCP Gateway Toolkit: Legal Criminal Dossier & Evidence (Canton de Vaud).
Exposes Swiss CPP legal tools with Invariant L-03 (Adriano Milli bona fide shield),
Art. 122 CPP victim protection (Arsen Kovalenko), and direct proxying to Node .234.
100% Pure Python Standard Library (ADR-002).
"""
import json
import logging
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

NODE_234_URL = "http://192.168.3.234:8766"

def _call_node_234(endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{NODE_234_URL}{endpoint}"
    req_body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        url,
        data=req_body,
        headers={"Content-Type": "application/json"} if req_body else {}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            return parsed.get("result", parsed)
    except Exception as e:
        return {"error": f"Failed to query Legal Node .234 ({url}): {e}"}

def legal_dossier_search(query: str, chapter: Optional[str] = None) -> Any:
    """Searches chapters in the Ukrainian/Swiss Legal Criminal Dossier (ED10 chapters 1 to 18)."""
    return _call_node_234("/api/tools/legal_dossier_search", {"query": query, "chapter": chapter})

def legal_transcripts_query(recording_id: Optional[str] = None, keyword: Optional[str] = None) -> Any:
    """Queries the 61 audio and phone message transcripts with exact timecodes and evidentiary tags."""
    return _call_node_234("/api/tools/legal_transcripts_query", {"recording_id": recording_id, "keyword": keyword})

def legal_actor_matrix_get() -> Any:
    """Returns all actors and formal procedural roles under Swiss CPP with Adriano Milli bona fide shield."""
    return _call_node_234("/api/tools/legal_actor_matrix_get", {})

def legal_evidence_get(evidence_id: Optional[str] = None) -> Any:
    """Retrieves physical and digital evidence records with SHA-256 hashes."""
    return _call_node_234("/api/tools/legal_evidence_get", {"evidence_id": evidence_id})

def legal_sprint_dispatch(sprint_id: str, instruction: str, prompt: Optional[str] = "") -> Any:
    """Dispatches an autonomous legal task/sprint for agy execution on Node .234."""
    return _call_node_234("/api/tools/legal_sprint_dispatch", {"sprint_id": sprint_id, "instruction": instruction, "prompt": prompt})

def legal_supervisor_status() -> Any:
    """Checks the operational status and active tasks of the Legal Supervisor daemon."""
    return _call_node_234("/api/tools/legal_supervisor_status", {})

def legal_epub_rebuild() -> Any:
    """Rebuilds test_dossier.epub containing full verified legal chapters."""
    return _call_node_234("/api/tools/legal_epub_rebuild", {})

def utopia_db_query(sql_query: str) -> Any:
    """Executes SQL query against the Utopia Bitemporal DB on host 192.168.3.251."""
    return _call_node_234("/api/tools/utopia_db_query", {"sql_query": sql_query})

def get_tools_spec() -> List[Dict[str, Any]]:
    return [
        {
            "name": "legal_dossier_search",
            "description": "Searches chapters in the Ukrainian/Swiss Legal Criminal Dossier (ED10 chapters 1 to 18) for articles (e.g. Art. 180, 138, 146 CP) or facts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text query, law article (e.g. Art. 146 CP), or actor name."},
                    "chapter": {"type": "string", "description": "Optional chapter filter (e.g. '01', '03', '12')."}
                },
                "required": ["query"]
            }
        },
        {
            "name": "legal_transcripts_query",
            "description": "Queries the 61 audio and phone message transcripts with exact timecodes and evidentiary tags.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "recording_id": {"type": "string", "description": "ID of the recording or timecode."},
                    "keyword": {"type": "string", "description": "Keyword search across conversation text."}
                }
            }
        },
        {
            "name": "legal_actor_matrix_get",
            "description": "Returns all actors and formal procedural roles under Swiss CPP with Adriano Milli bona fide shield (Invariant L-03).",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "legal_evidence_get",
            "description": "Retrieves physical and digital evidence records with SHA-256 hashes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "evidence_id": {"type": "string", "description": "Specific evidence ID (e.g. 'REC-001', 'DOC-012') or keyword."}
                }
            }
        },
        {
            "name": "legal_sprint_dispatch",
            "description": "Dispatches an autonomous legal task/sprint for agy execution on Node .234.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "string", "description": "Identifier for the sprint (e.g. 'sprint_003_legal')."},
                    "instruction": {"type": "string", "description": "Instruction for the sprint."},
                    "prompt": {"type": "string", "description": "Detailed prompt or context requirements."}
                },
                "required": ["sprint_id", "instruction"]
            }
        },
        {
            "name": "legal_supervisor_status",
            "description": "Checks the operational status and active tasks of the Legal Supervisor daemon.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "legal_epub_rebuild",
            "description": "Rebuilds test_dossier.epub containing full verified legal chapters.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "utopia_db_query",
            "description": "Executes SQL query against the Utopia Bitemporal DB on host 192.168.3.251.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql_query": {"type": "string", "description": "SQL statement (SELECT only recommended)."}
                },
                "required": ["sql_query"]
            }
        }
    ]
