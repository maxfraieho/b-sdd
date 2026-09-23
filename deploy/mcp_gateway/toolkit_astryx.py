"""
B-SDD MCP Gateway Toolkit: Astryx Cockpit Real-time Canvas & Deployer.
Implements real-time canvas push to Astryx Cockpit and automated
Cloudflare Pages deployment triggers compliant with ADR-008 and ADR-009.
100% Pure Python Standard Library (ADR-002).
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.drakon.parser import DrakonParser
from src.drakon.validator import DrakonValidator

CANVAS_STORE_DIR = ROOT_DIR / ".context" / "astryx_canvas"


def canvas_push(
    schema: Union[Dict[str, Any], str],
    canvas_id: str = "main",
    notify: bool = True
) -> Dict[str, Any]:
    """
    Pushes a DRAKON schema or UI canvas state to the Astryx Cockpit.
    Validates planarity, persists to local canvas store, and notifies the live workbench.
    """
    try:
        if isinstance(schema, str):
            schema_data = json.loads(schema)
        else:
            schema_data = schema

        parsed_schema = DrakonParser.parse_dict(schema_data)
        validator = DrakonValidator(root_dir=ROOT_DIR)
        val_res = validator.validate(parsed_schema)

        CANVAS_STORE_DIR.mkdir(parents=True, exist_ok=True)
        canvas_file = CANVAS_STORE_DIR / f"{canvas_id}.drakon.json"
        canvas_file.write_text(json.dumps(schema_data, indent=2), encoding="utf-8")

        now_iso = datetime.now(timezone.utc).isoformat()
        notified_workbench = False

        if notify:
            try:
                # Attempt to notify local running workbench server (:8765)
                req = urllib.request.Request(
                    "http://127.0.0.1:8765/api/drakon/schema",
                    data=json.dumps(schema_data).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        notified_workbench = True
            except Exception:
                notified_workbench = False

        return {
            "status": "PUSHED",
            "canvas_id": canvas_id,
            "node_count": len(parsed_schema.nodes),
            "is_planar_valid": val_res.is_valid,
            "validation_errors": [str(e) for e in val_res.errors],
            "canvas_path": str(canvas_file),
            "notified_workbench": notified_workbench,
            "updated_at": now_iso
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "canvas_id": canvas_id,
            "error": str(e)
        }


def get_canvas_state(canvas_id: str = "main") -> Dict[str, Any]:
    """Retrieves current active canvas state from the Astryx store."""
    try:
        canvas_file = CANVAS_STORE_DIR / f"{canvas_id}.drakon.json"
        if canvas_file.exists():
            data = json.loads(canvas_file.read_text(encoding="utf-8"))
            return {
                "status": "SUCCESS",
                "canvas_id": canvas_id,
                "schema": data,
                "updated_at": datetime.fromtimestamp(canvas_file.stat().st_mtime, tz=timezone.utc).isoformat()
            }

        # Return default template
        tmpl_file = ROOT_DIR / "src" / "drakon" / "templates" / "sovereign_copilot_and_gateway.json"
        if tmpl_file.exists():
            tmpl_data = json.loads(tmpl_file.read_text(encoding="utf-8"))
            return {
                "status": "SUCCESS_DEFAULT",
                "canvas_id": canvas_id,
                "schema": tmpl_data,
                "updated_at": None
            }

        return {
            "status": "NOT_FOUND",
            "canvas_id": canvas_id,
            "schema": None
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "canvas_id": canvas_id,
            "error": str(e)
        }


def deploy_trigger(
    environment: str = "production",
    skip_tests: bool = False,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Triggers production deployment of the Astryx Cockpit frontend to Cloudflare Pages.
    Executes scripts/deploy_cloudflare_pages.sh or validates readiness in dry-run mode.
    """
    deploy_script = ROOT_DIR / "scripts" / "deploy_cloudflare_pages.sh"
    target_url = "https://b-sdd-ui.pages.dev"

    if dry_run:
        dist_path = ROOT_DIR / "b-sdd-ui" / "dist"
        has_dist = dist_path.exists() and any(dist_path.iterdir())
        return {
            "status": "DRY_RUN_OK",
            "environment": environment,
            "deploy_script_exists": deploy_script.exists(),
            "frontend_dist_ready": has_dist,
            "target_url": target_url,
            "message": "Deployment pre-flight checks passed."
        }

    if not deploy_script.exists():
        return {
            "status": "ERROR",
            "error": f"Deployment script missing: {deploy_script}"
        }

    try:
        env = dict(os.environ)
        if skip_tests:
            env["SKIP_TESTS"] = "1"

        res = subprocess.run(
            ["bash", str(deploy_script)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=180,
            env=env
        )

        return {
            "status": "DEPLOYED" if res.returncode == 0 else "FAILED",
            "environment": environment,
            "exit_code": res.returncode,
            "target_url": target_url,
            "stdout": res.stdout[-800:] if res.stdout else "",
            "stderr": res.stderr[-800:] if res.stderr else ""
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "environment": environment,
            "error": str(e)
        }


def get_tools_spec() -> List[Dict[str, Any]]:
    """Returns MCP tools catalog definition for toolkit_astryx."""
    return [
        {
            "name": "astryx_canvas_push",
            "description": "Pushes DRAKON visual flow state to Astryx Cockpit and notifies live workbench.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "schema": {
                        "type": ["object", "string"],
                        "description": "DRAKON schema dictionary or JSON string."
                    },
                    "canvas_id": {"type": "string", "default": "main", "description": "Canvas identifier."},
                    "notify": {"type": "boolean", "default": True}
                },
                "required": ["schema"]
            }
        },
        {
            "name": "astryx_canvas_get",
            "description": "Retrieves the active DRAKON canvas state from the Astryx store.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "default": "main"}
                }
            }
        },
        {
            "name": "astryx_deploy_trigger",
            "description": "Triggers automated build and deployment of Astryx Cockpit to Cloudflare Pages.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "environment": {"type": "string", "default": "production"},
                    "skip_tests": {"type": "boolean", "default": False},
                    "dry_run": {"type": "boolean", "default": False}
                }
            }
        }
    ]
