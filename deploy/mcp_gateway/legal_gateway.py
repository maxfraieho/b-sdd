"""
B-SDD Legal Sovereign Remote MCP Gateway v1.0.
Dedicated Legal MCP Gateway on Node 192.168.3.161 / Port 8766.
Exposes Swiss CPP legal tools, Utopia DB, GitNexus, and DRAKON to Gemini Spark & Google AI.
Fully compliant with MCP Specification 2024-11-05 (SSE, Streamable HTTP, JSON-RPC 2.0).
"""
import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# Ensure repo root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Toolkits
from deploy.mcp_gateway import (
    toolkit_legal,
    toolkit_docs,
    toolkit_utopia,
    toolkit_gitnexus,
    toolkit_drakon,
    toolkit_astryx,
    toolkit_skills,
)

CONFIG_PATH = Path(__file__).resolve().parent / "legal_config.json"


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Failed to parse {CONFIG_PATH}: {e}", file=sys.stderr)
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 8766,
            "bearer_token": "",
            "auth_enabled": False,
            "require_auth": False
        },
        "cors": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        },
        "upstreams": {
            "legal_node": "http://192.168.3.234:8766",
            "utopia_db": "http://192.168.3.251:9622",
            "laya_engine": "http://192.168.3.251:9623",
            "gitnexus": "http://192.168.3.184:4747",
            "sovereign_llm": "http://192.168.3.184:18880",
            "b_sdd_core": "http://127.0.0.1:8765"
        }
    }


CONFIG = load_config()
SERVER_HOST = os.environ.get("LEGAL_MCP_HOST", CONFIG.get("server", {}).get("host", "0.0.0.0"))
SERVER_PORT = int(os.environ.get("LEGAL_MCP_PORT", CONFIG.get("server", {}).get("port", 8766)))

app = FastAPI(
    title="B-SDD Legal Sovereign Remote MCP Gateway",
    version="1.0.0",
    description="Sovereign MCP gateway exposing Swiss Criminal Legal tools, Utopia DB, GitNexus, and DRAKON."
)

# Universal CORS Headers for MCP / Web / Gemini Spark
CORS_HEADERS: Dict[str, str] = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS, HEAD, PUT, DELETE",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Max-Age": "86400",
}

# Standard Starlette CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def cors_and_probe_middleware(request: Request, call_next):
    """Intercepts OPTIONS and injects universal CORS headers into all responses."""
    if request.method == "OPTIONS":
        return Response(status_code=200, content="", media_type="text/plain", headers=CORS_HEADERS)

    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


# Active SSE Sessions
ACTIVE_SESSIONS: Dict[str, asyncio.Queue] = {}



def get_all_tool_specs() -> List[Dict[str, Any]]:
    """Aggregates all tool specifications across legal and core toolkits."""
    tools = []
    # 1. Legal tools (Primary)
    tools.extend(toolkit_legal.get_tools_spec())
    # 2. Documentation & Architecture Planning tools (Spark Architect)
    tools.extend(toolkit_docs.get_tools_spec())
    # 3. Utopia DB tools
    tools.extend(toolkit_utopia.get_tools_spec())
    # 4. GitNexus AST tools
    tools.extend(toolkit_gitnexus.get_tools_spec())
    # 5. DRAKON tools
    tools.extend(toolkit_drakon.get_tools_spec())
    # 6. Astryx tools
    tools.extend(toolkit_astryx.get_tools_spec())
    # 7. System Skills
    tools.extend(toolkit_skills.get_tools_spec())
    return tools


def dispatch_tool_call(name: str, args: Dict[str, Any]) -> Any:
    """Dispatches tool execution to the appropriate toolkit."""
    # 1. Legal Tools
    if name == "legal_dossier_search":
        return toolkit_legal.legal_dossier_search(query=args.get("query", ""), chapter=args.get("chapter"))
    elif name == "legal_transcripts_query":
        return toolkit_legal.legal_transcripts_query(recording_id=args.get("recording_id"), keyword=args.get("keyword"))
    elif name == "legal_actor_matrix_get":
        return toolkit_legal.legal_actor_matrix_get()
    elif name == "legal_evidence_get":
        return toolkit_legal.legal_evidence_get(evidence_id=args.get("evidence_id"))
    elif name == "legal_sprint_dispatch":
        return toolkit_legal.legal_sprint_dispatch(sprint_id=args.get("sprint_id", "sprint_003"), instruction=args.get("instruction", ""), prompt=args.get("prompt"))
    elif name == "legal_supervisor_status":
        return toolkit_legal.legal_supervisor_status()
    elif name == "legal_epub_rebuild":
        return toolkit_legal.legal_epub_rebuild()
    elif name == "utopia_db_query":
        return toolkit_legal.utopia_db_query(sql_query=args.get("sql_query", ""))

    # 2. Documentation & Planning Tools (Spark Architect)
    elif name == "legal_docs_list":
        return toolkit_docs.docs_list(category=args.get("category", "all"))
    elif name == "legal_docs_read":
        return toolkit_docs.docs_read(doc_path=args.get("doc_path", ""), max_chars=args.get("max_chars"))
    elif name == "legal_docs_write":
        return toolkit_docs.docs_write(
            doc_path=args.get("doc_path", ""),
            content=args.get("content", ""),
            mode=args.get("mode", "overwrite"),
            author=args.get("author", "Gemini Spark Architect"),
            comment=args.get("comment")
        )
    elif name == "legal_plan_save":
        return toolkit_docs.plan_save(
            plan_id=args.get("plan_id", ""),
            title=args.get("title", ""),
            objective=args.get("objective", ""),
            content=args.get("content", ""),
            steps=args.get("steps"),
            status=args.get("status", "DRAFT"),
            tags=args.get("tags"),
            author=args.get("author", "Gemini Spark Architect")
        )
    elif name == "legal_plans_list":
        return toolkit_docs.plans_list(status=args.get("status"), tag=args.get("tag"))
    elif name == "legal_plan_get":
        return toolkit_docs.plan_get(plan_id=args.get("plan_id", ""))

    # 2. Utopia Tools
    elif name == "utopia_bitemporal_query":
        return toolkit_utopia.bitemporal_query(valid_time_day=args.get("valid_time_day"), component=args.get("component"), sql=args.get("sql"))
    elif name == "utopia_record_worm_ledger":
        return toolkit_utopia.record_worm_ledger(
            sprint_id=args.get("sprint_id", "sprint_legal"),
            commit_hash=args.get("commit_hash", ""),
            release_tag=args.get("release_tag", ""),
            phase=args.get("phase", "PHI_7_DISTILLED"),
            rules_word_count=args.get("rules_word_count"),
            metadata=args.get("metadata")
        )
    elif name == "utopia_check_invariants":
        return toolkit_utopia.check_invariants(component=args.get("component"))

    # 3. GitNexus AST Tools
    elif name == "gitnexus_ast_query":
        return toolkit_gitnexus.query_ast_graph(query_type=args.get("query_type", "cross_repo"), valid_time_day=args.get("valid_time_day"), params=args.get("params"))
    elif name == "gitnexus_blast_radius":
        return toolkit_gitnexus.audit_blast_radius(symbol_name=args.get("symbol_name", ""), max_depth=args.get("max_depth", 3), files=args.get("files"))
    elif name == "gitnexus_symbol_search":
        return toolkit_gitnexus.symbol_search(query=args.get("query", ""), workspace=args.get("workspace"), symbol_type=args.get("symbol_type"), limit=args.get("limit", 50))

    # 4. DRAKON Tools
    elif name == "drakon_planar_validate":
        return toolkit_drakon.planar_validate(args.get("schema_input", args.get("schema", {})))
    elif name == "drakon_svg_export":
        return toolkit_drakon.svg_export(schema_input=args.get("schema_input", args.get("schema", {})), title=args.get("title", "DRAKON Diagram"))
    elif name == "drakon_code_compile":
        return toolkit_drakon.compile_code(schema_input=args.get("schema_input", args.get("schema", {})), target_lang=args.get("target_lang", "pseudocode"))

    # 5. Astryx Tools
    elif name == "astryx_canvas_push":
        return toolkit_astryx.canvas_push(schema=args.get("schema", {}), canvas_id=args.get("canvas_id", "main"), notify=args.get("notify", True))
    elif name == "astryx_canvas_get":
        return toolkit_astryx.get_canvas_state(canvas_id=args.get("canvas_id", "main"))

    # 6. Skills Tools
    elif name == "skills_catalog_inspect":
        return toolkit_skills.inspect_skills_catalog(category=args.get("category"), search=args.get("search"), include_drakon=args.get("include_drakon", False))
    elif name == "skills_rule_of_two_crystallize":
        return toolkit_skills.crystallize_rule_of_two(skill_name=args.get("skill_name", ""), session_id=args.get("session_id"), user_prompt=args.get("user_prompt"), dry_run=args.get("dry_run", False))
    elif name == "skills_verify_immutability":
        return toolkit_skills.verify_immutability()

    raise ValueError(f"Unknown tool: {name}")


def process_jsonrpc_request(req_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Processes incoming JSON-RPC 2.0 messages compliant with MCP 2024-11-05."""
    rpc_id = req_data.get("id")
    method = req_data.get("method")
    params = req_data.get("params", {})

    if not method:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32600, "message": "Invalid Request: missing method"}
        }

    # Initialize Handshake
    if method == "initialize":
        client_version = params.get("protocolVersion", "2024-11-05")
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": client_version,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "logging": {},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "b-sdd-legal-mcp",
                    "version": "1.0.0"
                }
            }
        }

    elif method in ("notifications/initialized", "initialized") or (rpc_id is None and method.startswith("notifications/")):
        return None

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {}}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"resources": []}}

    elif method == "prompts/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"prompts": []}}

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {"tools": get_all_tool_specs()}
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            res = dispatch_tool_call(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res, indent=2, ensure_ascii=False) if not isinstance(res, str) else res
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error executing tool '{tool_name}': {str(e)}"}],
                    "isError": True
                }
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


# ------------------------------------------------------------------------------
# URL RESOLUTION (Absolute URL for Google AI Studio / Gemini Spark)
# ------------------------------------------------------------------------------

def resolve_public_base_url(request: Request) -> str:
    """Computes the external public base URL for Google AI Studio / Gemini Spark."""
    forwarded_proto = request.headers.get("x-forwarded-proto") or request.headers.get("x-forwarded-protocol")
    forwarded_host = request.headers.get("x-forwarded-host")
    host_header = request.headers.get("host")

    if forwarded_host:
        proto = forwarded_proto or "https"
        return f"{proto}://{forwarded_host}".rstrip("/")
    if host_header:
        if "legal-mcp.exodus.pp.ua" in host_header:
            return "https://legal-mcp.exodus.pp.ua"
        proto = forwarded_proto or ("https" if "exodus.pp.ua" in host_header else request.url.scheme)
        return f"{proto}://{host_header}".rstrip("/")
    return "https://legal-mcp.exodus.pp.ua"


# ------------------------------------------------------------------------------
# HEAD & OPTIONS PROBE HANDLERS (Critical for Gemini Spark & Cloudflare validation)
# ------------------------------------------------------------------------------

@app.options("/{full_path:path}")
def global_options_handler(full_path: str):
    return Response(status_code=200, content="", media_type="text/plain", headers=CORS_HEADERS)


@app.options("/")
@app.options("/health")
@app.options("/sse")
@app.options("/mcp")
@app.options("/messages")
@app.options("/mcp/messages")
@app.options("/rpc")
def explicit_options_handler():
    return Response(status_code=200, content="", media_type="text/plain", headers=CORS_HEADERS)


@app.head("/")
@app.head("/health")
def root_and_health_head():
    return Response(status_code=200, media_type="application/json", headers=CORS_HEADERS)


@app.head("/sse")
@app.head("/mcp")
def sse_head():
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream; charset=utf-8",
    }
    headers.update(CORS_HEADERS)
    return Response(status_code=200, headers=headers)


@app.head("/messages")
@app.head("/mcp/messages")
@app.head("/rpc")
def rpc_head():
    return Response(status_code=200, media_type="application/json", headers=CORS_HEADERS)


# ------------------------------------------------------------------------------
# HTTP & SSE ENDPOINTS
# ------------------------------------------------------------------------------

@app.get("/")
def root_info():
    return {
        "service": "b-sdd-legal-mcp",
        "protocol": "mcp",
        "version": "1.0.0",
        "sse_endpoint": "/sse",
        "mcp_endpoint": "/mcp",
        "tools_count": len(get_all_tool_specs())
    }


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": "b-sdd-legal-mcp",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tools_count": len(get_all_tool_specs()),
        "upstreams": CONFIG.get("upstreams", {})
    }


@app.get("/sse")
@app.get("/mcp")
async def sse_transport(request: Request):
    """
    Standard MCP SSE Transport Endpoint.
    Opens persistent SSE connection, yields the message endpoint with ABSOLUTE URL, and keeps alive.
    Supports /sse and /mcp aliases with dual sessionId and session_id parameter formats.
    """
    session_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    ACTIVE_SESSIONS[session_id] = queue

    base_url = resolve_public_base_url(request)
    endpoint_path = "/mcp/messages" if request.url.path.startswith("/mcp") else "/messages"
    endpoint_full_url = f"{base_url}{endpoint_path}?sessionId={session_id}&session_id={session_id}"

    async def sse_generator():
        try:
            yield f"event: endpoint\ndata: {endpoint_full_url}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    if await request.is_disconnected():
                        break
                    yield ": keepalive\n\n"
        finally:
            ACTIVE_SESSIONS.pop(session_id, None)

    resp_headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    resp_headers.update(CORS_HEADERS)
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers=resp_headers
    )


@app.post("/messages")
@app.post("/mcp/messages")
async def sse_messages(
    request: Request,
    session_id: Optional[str] = Query(None),
    sessionId: Optional[str] = Query(None)
):
    """Handles incoming JSON-RPC 2.0 requests over SSE transport."""
    actual_session_id = sessionId or session_id or request.headers.get("mcp-session-id")
    try:
        req_json = await request.json()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {e}"}},
            headers=CORS_HEADERS
        )
    resp = process_jsonrpc_request(req_json)

    headers = dict(CORS_HEADERS)
    if actual_session_id:
        headers["Mcp-Session-Id"] = actual_session_id

    if actual_session_id and actual_session_id in ACTIVE_SESSIONS and resp is not None:
        await ACTIVE_SESSIONS[actual_session_id].put(resp)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "QUEUED_TO_SSE"}, headers=headers)

    return JSONResponse(content=resp or {}, headers=headers)


@app.post("/rpc")
@app.post("/")
@app.post("/mcp")
@app.post("/sse")
async def direct_rpc(
    request: Request,
    session_id: Optional[str] = Query(None),
    sessionId: Optional[str] = Query(None)
):
    """Direct HTTP POST JSON-RPC 2.0 and Streamable HTTP handler."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        )

    actual_session_id = sessionId or session_id or request.headers.get("mcp-session-id")

    if isinstance(body, list):
        responses = [process_jsonrpc_request(item) for item in body]
        resp_content = [r for r in responses if r is not None]
    else:
        resp_content = process_jsonrpc_request(body)

    if actual_session_id and actual_session_id in ACTIVE_SESSIONS and resp_content:
        await ACTIVE_SESSIONS[actual_session_id].put(resp_content)

    headers = {"Access-Control-Allow-Origin": "*"}
    if actual_session_id:
        headers["Mcp-Session-Id"] = actual_session_id

    return JSONResponse(content=resp_content or {}, headers=headers)


@app.get("/api/tools")
def list_tools(request: Request):
    """REST endpoint to inspect all registered MCP tools."""
    return {"tools": get_all_tool_specs()}


if __name__ == "__main__":
    uvicorn.run(
        "deploy.mcp_gateway.legal_gateway:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
        reload=False
    )
