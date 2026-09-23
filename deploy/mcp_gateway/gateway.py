"""
B-SDD Universal Remote MCP Gateway (Sprint 036).
Provides a sovereign Model Context Protocol (MCP) gateway over HTTP/SSE and JSON-RPC 2.0
with Bearer token authentication, CORS support, and seamless tool proxying
to Astryx, DRAKON, GitNexus, Skills, and Utopia DB ecosystems.
"""
import asyncio
import json
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
from pydantic import BaseModel, Field

# Ensure repo root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Toolkits
from deploy.mcp_gateway import (
    toolkit_astryx,
    toolkit_drakon,
    toolkit_gitnexus,
    toolkit_skills,
    toolkit_utopia,
)

# Load configuration
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Failed to parse {CONFIG_PATH}: {e}", file=sys.stderr)
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 8765,
            "bearer_token": "bsdd-sovereign-mcp-key-sprint-036"
        },
        "cors": {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"]
        },
        "upstreams": {
            "utopia_db": "http://192.168.3.251:9622",
            "laya_engine": "http://192.168.3.251:9623",
            "gitnexus": "http://192.168.3.184:4747",
            "sovereign_llm": "http://192.168.3.184:18880",
            "astryx_ui": "http://127.0.0.1:5173",
            "supervisor": "http://127.0.0.1:8161"
        }
    }


CONFIG = load_config()
SERVER_HOST = os.environ.get("MCP_GATEWAY_HOST", CONFIG.get("server", {}).get("host", "0.0.0.0"))
SERVER_PORT = int(os.environ.get("MCP_GATEWAY_PORT", CONFIG.get("server", {}).get("port", 8765)))
CONFIGURED_BEARER_TOKEN = os.environ.get("MCP_BEARER_TOKEN", CONFIG.get("server", {}).get("bearer_token", ""))

app = FastAPI(
    title="B-SDD Universal Remote MCP Gateway",
    version="1.0.0",
    description="Sovereign MCP gateway exposing Astryx, DRAKON, GitNexus, Skills, and Utopia DB tools."
)

# CORS
cors_cfg = CONFIG.get("cors", {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_cfg.get("allow_origins", ["*"]),
    allow_credentials=cors_cfg.get("allow_credentials", True),
    allow_methods=cors_cfg.get("allow_methods", ["*"]),
    allow_headers=cors_cfg.get("allow_headers", ["*"]),
)

# Active SSE Sessions
ACTIVE_SESSIONS: Dict[str, asyncio.Queue] = {}


# Auth Dependency
def verify_bearer_auth(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
):
    if not CONFIGURED_BEARER_TOKEN:
        return True  # No token configured, open access

    provided = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            provided = parts[1]
        elif len(parts) == 1:
            provided = parts[0]
    elif token:
        provided = token

    if not provided or provided != CONFIGURED_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Bearer token authentication.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


# ------------------------------------------------------------------------------
# Tool Handlers and Proxies
# ------------------------------------------------------------------------------

def handle_drakon_schema_astryx_sync(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Composite tool: Validates DRAKON schema planarity and synchronizes
    canvas state directly with Astryx Cockpit and workbench server.
    """
    schema = args.get("schema")
    if not schema:
        return {"status": "ERROR", "error": "Missing 'schema' in arguments."}

    canvas_id = args.get("canvas_id", "main")
    notify = args.get("notify", True)

    # 1. Planar validation
    planarity = toolkit_drakon.planar_validate(schema)

    # 2. Push to canvas
    push_res = toolkit_astryx.canvas_push(schema=schema, canvas_id=canvas_id, notify=notify)

    return {
        "status": "SUCCESS" if push_res.get("status") == "PUSHED" else "ERROR",
        "tool": "drakon_schema_astryx_sync",
        "canvas_id": canvas_id,
        "planarity": planarity,
        "canvas_sync": push_res,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def handle_utopia_worm_append(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appends an immutable audit transaction to the sovereign Utopia WORM ledger.
    """
    sprint_id = args.get("sprint_id", "sprint_036")
    commit_hash = args.get("commit_hash", "HEAD")
    if commit_hash == "HEAD":
        import subprocess
        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=str(ROOT_DIR), text=True
            ).strip()
        except Exception:
            commit_hash = "0000000000000000000000000000000000000000"

    release_tag = args.get("release_tag", f"{sprint_id}_done")
    phase = args.get("phase", "PHI_7_DISTILLED")
    rules_word_count = args.get("rules_word_count")
    metadata = args.get("metadata", {})
    metadata["recorded_via"] = "bsdd-mcp-gateway"

    res = toolkit_utopia.record_worm_ledger(
        sprint_id=sprint_id,
        commit_hash=commit_hash,
        release_tag=release_tag,
        phase=phase,
        rules_word_count=rules_word_count,
        metadata=metadata
    )
    return {
        "status": "SUCCESS" if res.get("status") == "COMMITTED" else "PARTIAL",
        "tool": "utopia_worm_append",
        "worm_result": res,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def handle_gitnexus_ast_impact_query(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Queries the GitNexus AST knowledge graph and audits blast radius for symbols or queries.
    """
    symbol_name = args.get("symbol_name")
    if symbol_name:
        max_depth = int(args.get("max_depth", 3))
        files = args.get("files")
        return toolkit_gitnexus.audit_blast_radius(symbol_name=symbol_name, max_depth=max_depth, files=files)

    query_type = args.get("query_type", "cross_repo")
    valid_time_day = args.get("valid_time_day")
    params = args.get("params")
    return toolkit_gitnexus.query_ast_graph(query_type=query_type, valid_time_day=valid_time_day, params=params)


# Master Dispatch Registry
CORE_TOOLS_SPEC: List[Dict[str, Any]] = [
    {
        "name": "drakon_schema_astryx_sync",
        "description": "Validates DRAKON planar schema and synchronizes canvas state to Astryx Cockpit (:8765).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "schema": {"type": "object", "description": "DRAKON schema object or JSON string."},
                "canvas_id": {"type": "string", "default": "main", "description": "Target canvas identifier."},
                "notify": {"type": "boolean", "default": True, "description": "Notify workbench server of canvas update."}
            },
            "required": ["schema"]
        }
    },
    {
        "name": "utopia_worm_append",
        "description": "Appends an immutable WORM transaction to Utopia DB ledger and local chain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {"type": "string", "description": "Sprint identifier (e.g. 'sprint_036')."},
                "commit_hash": {"type": "string", "default": "HEAD", "description": "Git commit hash."},
                "release_tag": {"type": "string", "description": "Release tag (e.g. 'sprint_036_done')."},
                "phase": {"type": "string", "default": "PHI_7_DISTILLED", "description": "Sprint lifecycle phase."},
                "rules_word_count": {"type": "integer", "description": "Active rules word count."},
                "metadata": {"type": "object", "description": "Additional telemetry metadata."}
            },
            "required": ["sprint_id"]
        }
    },
    {
        "name": "gitnexus_ast_impact_query",
        "description": "Audits blast radius or queries GitNexus AST knowledge graph for dependencies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol_name": {"type": "string", "description": "Symbol name for blast radius audit."},
                "max_depth": {"type": "integer", "default": 3, "description": "Max call graph traversal depth."},
                "query_type": {"type": "string", "enum": ["cross_repo", "raw"], "default": "cross_repo"},
                "valid_time_day": {"type": "integer", "description": "Optional temporal day snapshot."}
            }
        }
    }
]


def get_all_tool_specs() -> List[Dict[str, Any]]:
    tools = list(CORE_TOOLS_SPEC)
    tools.extend(toolkit_astryx.get_tools_spec())
    tools.extend(toolkit_drakon.get_tools_spec())
    tools.extend(toolkit_gitnexus.get_tools_spec())
    tools.extend(toolkit_skills.get_tools_spec())
    tools.extend(toolkit_utopia.get_tools_spec())
    return tools


def dispatch_tool_call(name: str, args: Dict[str, Any]) -> Any:
    # 1. Check core composite tools
    if name == "drakon_schema_astryx_sync":
        return handle_drakon_schema_astryx_sync(args)
    elif name == "utopia_worm_append":
        return handle_utopia_worm_append(args)
    elif name == "gitnexus_ast_impact_query":
        return handle_gitnexus_ast_impact_query(args)

    # 2. Astryx tools
    elif name == "astryx_canvas_push":
        return toolkit_astryx.canvas_push(schema=args.get("schema", {}), canvas_id=args.get("canvas_id", "main"), notify=args.get("notify", True))
    elif name == "astryx_canvas_get":
        return toolkit_astryx.get_canvas_state(canvas_id=args.get("canvas_id", "main"))
    elif name == "astryx_deploy_trigger":
        return toolkit_astryx.deploy_trigger(environment=args.get("environment", "production"), run_build=args.get("run_build", True))

    # 3. DRAKON tools
    elif name == "drakon_planar_validate":
        return toolkit_drakon.planar_validate(args.get("schema_input", args.get("schema", {})))
    elif name == "drakon_svg_export":
        return toolkit_drakon.svg_export(schema_input=args.get("schema_input", args.get("schema", {})), title=args.get("title", "DRAKON Diagram"))
    elif name == "drakon_code_compile":
        return toolkit_drakon.compile_code(schema_input=args.get("schema_input", args.get("schema", {})), target_lang=args.get("target_lang", "pseudocode"))
    elif name == "drakon_macro_flow_synthesis":
        return toolkit_drakon.macro_flow_synthesis(steps=args.get("steps", []), title=args.get("title", "Synthesized Flow"))

    # 4. GitNexus tools
    elif name == "gitnexus_ast_query":
        return toolkit_gitnexus.query_ast_graph(query_type=args.get("query_type", "cross_repo"), valid_time_day=args.get("valid_time_day"), params=args.get("params"))
    elif name == "gitnexus_blast_radius":
        return toolkit_gitnexus.audit_blast_radius(symbol_name=args.get("symbol_name", ""), max_depth=args.get("max_depth", 3), files=args.get("files"))
    elif name == "gitnexus_symbol_search":
        return toolkit_gitnexus.symbol_search(query=args.get("query", ""), workspace=args.get("workspace"), symbol_type=args.get("symbol_type"), limit=args.get("limit", 50))

    # 5. Skills tools
    elif name == "skills_catalog_inspect":
        return toolkit_skills.inspect_skills_catalog(category=args.get("category"), search=args.get("search"), include_drakon=args.get("include_drakon", False))
    elif name == "skills_rule_of_two_crystallize":
        return toolkit_skills.crystallize_rule_of_two(skill_name=args.get("skill_name", ""), session_id=args.get("session_id"), user_prompt=args.get("user_prompt"), dry_run=args.get("dry_run", False))
    elif name == "skills_verify_immutability":
        return toolkit_skills.verify_immutability()

    # 6. Utopia DB tools
    elif name == "utopia_bitemporal_query":
        return toolkit_utopia.bitemporal_query(valid_time_day=args.get("valid_time_day"), component=args.get("component"), sql=args.get("sql"))
    elif name == "utopia_record_worm_ledger":
        return toolkit_utopia.record_worm_ledger(
            sprint_id=args.get("sprint_id", "sprint_036"),
            commit_hash=args.get("commit_hash", ""),
            release_tag=args.get("release_tag", ""),
            phase=args.get("phase", "PHI_7_DISTILLED"),
            rules_word_count=args.get("rules_word_count"),
            metadata=args.get("metadata")
        )
    elif name == "utopia_check_invariants":
        return toolkit_utopia.check_invariants(component=args.get("component"))

    else:
        raise ValueError(f"Unknown MCP tool: {name}")


# ------------------------------------------------------------------------------
# JSON-RPC 2.0 Engine
# ------------------------------------------------------------------------------

def process_jsonrpc_request(req_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rpc_id = req_data.get("id")
    method = req_data.get("method")
    params = req_data.get("params", {})

    if not method:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32600, "message": "Invalid Request: missing method"}
        }

    # Standard MCP Methods
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "b-sdd-mcp-gateway",
                    "version": "1.0.0"
                }
            }
        }

    elif method in ("notifications/initialized", "initialized"):
        # Notifications don't return responses in JSON-RPC
        return None

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {}}

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
                            "text": json.dumps(res, indent=2, ensure_ascii=False)
                        }
                    ],
                    "isError": False if isinstance(res, dict) and res.get("status") != "ERROR" else False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing tool '{tool_name}': {str(e)}"
                        }
                    ],
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
# HTTP & SSE Endpoints
# ------------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Health status and registered tools inventory."""
    return {
        "status": "UP",
        "service": "b-sdd-mcp-gateway",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tools_count": len(get_all_tool_specs()),
        "upstreams": CONFIG.get("upstreams", {})
    }


@app.get("/sse")
async def sse_transport(
    request: Request
):
    """
    Standard MCP SSE Transport Endpoint.
    Opens persistent SSE connection, yields the message endpoint, and keeps alive.
    """
    verify_bearer_auth(
        authorization=request.headers.get("authorization"),
        token=request.query_params.get("token")
    )
    session_id = str(uuid.uuid4())
    queue: asyncio.Queue = asyncio.Queue()
    ACTIVE_SESSIONS[session_id] = queue

    async def sse_generator():
        try:
            # Yield initial endpoint event compliant with MCP SSE spec
            yield f"event: endpoint\ndata: /messages?session_id={session_id}\n\n"
            while True:
                # Check for outgoing messages or yield keep-alive ping
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    if await request.is_disconnected():
                        break
                    yield ": keepalive\n\n"
        finally:
            ACTIVE_SESSIONS.pop(session_id, None)

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/messages")
async def sse_messages(
    request: Request,
    session_id: Optional[str] = Query(None)
):
    """
    Handles incoming JSON-RPC 2.0 requests over SSE transport.
    """
    verify_bearer_auth(
        authorization=request.headers.get("authorization"),
        token=request.query_params.get("token")
    )
    req_json = await request.json()
    resp = process_jsonrpc_request(req_json)

    if session_id and session_id in ACTIVE_SESSIONS and resp is not None:
        await ACTIVE_SESSIONS[session_id].put(resp)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "QUEUED_TO_SSE"})

    return JSONResponse(content=resp or {})


@app.post("/rpc")
@app.post("/")
async def direct_rpc(request: Request):
    """
    Direct HTTP POST JSON-RPC 2.0 handler.
    """
    verify_bearer_auth(
        authorization=request.headers.get("authorization"),
        token=request.query_params.get("token")
    )
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        )

    if isinstance(body, list):
        responses = [process_jsonrpc_request(item) for item in body]
        return JSONResponse(content=[r for r in responses if r is not None])
    else:
        resp = process_jsonrpc_request(body)
        return JSONResponse(content=resp or {})


@app.get("/api/tools")
def list_tools(request: Request):
    """REST endpoint to inspect all registered MCP tools."""
    verify_bearer_auth(
        authorization=request.headers.get("authorization"),
        token=request.query_params.get("token")
    )
    return {"tools": get_all_tool_specs()}


@app.post("/api/tools/{tool_name}")
async def invoke_tool_rest(tool_name: str, request: Request):
    """REST endpoint to directly invoke any MCP tool."""
    verify_bearer_auth(
        authorization=request.headers.get("authorization"),
        token=request.query_params.get("token")
    )
    try:
        args = await request.json() if (await request.body()) else {}
    except Exception:
        args = {}

    try:
        res = dispatch_tool_call(tool_name, args)
        return JSONResponse(content={"status": "SUCCESS", "tool": tool_name, "result": res})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "ERROR", "tool": tool_name, "error": str(e)}
        )


if __name__ == "__main__":
    print(f"🚀 Starting B-SDD Universal Remote MCP Gateway on http://{SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
