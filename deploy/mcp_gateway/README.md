# B-SDD Universal Remote MCP Gateway (Sprint 036)

Sovereign **Model Context Protocol (MCP)** Gateway designed for B-SDD (Bitemporal Spec-Driven Development), exposing unified tools across Astryx, DRAKON, GitNexus, Skills, and Utopia DB ecosystems.

Compliant with **ADR-001, ADR-002, ADR-004, ADR-008, ADR-015, and ADR-016**.

---

## 1. Architecture & Capabilities

- **Protocols Supported**:
  - **SSE Transport**: `GET /sse` with standard MCP session endpoints.
  - **JSON-RPC 2.0**: `POST /messages?session_id=...`, `POST /rpc`, and `POST /`.
  - **REST Direct API**: `GET /api/tools` and `POST /api/tools/{tool_name}`.
- **Security & Network**:
  - Bearer Token Authentication via `Authorization: Bearer <token>` or `?token=<token>`.
  - CORS headers configurable for local and Cloudflare Pages origins.
  - Port `8765` binding with zero external service drift.
- **Ecosystem Proxies**:
  - **Utopia DB**: `http://192.168.3.251:9622` (Bitemporal Tv/Tx, WORM Ledger).
  - **Laya System 1**: `http://192.168.3.251:9623` (Podroid Decision Engine).
  - **GitNexus Graph**: `http://192.168.3.184:4747` (KuzuDB AST Code Intelligence).
  - **Sovereign LLM**: `http://192.168.3.184:18880` (v1/chat/completions).

---

## 2. Registered Tool Inventory (19 Tools)

### Core Composite Proxy Tools
1. `drakon_schema_astryx_sync`: Validates DRAKON planar schema and synchronizes canvas state to Astryx Cockpit (`:8765`).
2. `utopia_worm_append`: Appends immutable WORM transactions to Utopia DB ledger and local chain.
3. `gitnexus_ast_impact_query`: Audits blast radius or queries GitNexus AST knowledge graph for dependencies.

### Domain Toolkits
- **Astryx Toolkit** (`toolkit_astryx.py`):
  - `astryx_canvas_push`
  - `astryx_canvas_get`
  - `astryx_deploy_trigger`
- **DRAKON Toolkit** (`toolkit_drakon.py`):
  - `drakon_planar_validate`
  - `drakon_svg_export`
  - `drakon_code_compile`
  - `drakon_macro_flow_synthesis`
- **GitNexus Toolkit** (`toolkit_gitnexus.py`):
  - `gitnexus_ast_query`
  - `gitnexus_blast_radius`
  - `gitnexus_symbol_search`
- **Skills Toolkit** (`toolkit_skills.py`):
  - `skills_catalog_inspect`
  - `skills_rule_of_two_crystallize`
  - `skills_verify_immutability`
- **Utopia Toolkit** (`toolkit_utopia.py`):
  - `utopia_bitemporal_query`
  - `utopia_record_worm_ledger`
  - `utopia_check_invariants`

---

## 3. Configuration (`config.json`)

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8765,
    "bearer_token": "bsdd-sovereign-mcp-key-sprint-036"
  },
  "cors": {
    "allow_origins": ["*"],
    "allow_credentials": true,
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
```

---

## 4. Quick Start & Execution

### Direct Execution
```bash
python3 deploy/mcp_gateway/gateway.py
```

### Systemd Service Setup
```bash
cp deploy/mcp_gateway/systemd/bsdd-mcp-gateway.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now bsdd-mcp-gateway.service
```

### Verification
```bash
curl -s http://127.0.0.1:8765/health | jq .
```
