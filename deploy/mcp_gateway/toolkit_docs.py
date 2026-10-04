"""
B-SDD Sovereign MCP Gateway Toolkit: Documentation & Architecture Planning.
Enables AI Architects (Gemini Spark / Google AI Studio / Claude / agy) to:
1. Browse and read all architectural specifications, ADRs, and guides across B-SDD and Legal Cockpit.
2. Create and update system documentation directly in docs/.
3. Formulate, save, list, and retrieve structured implementation plans in docs/plans/.

100% Pure Python Standard Library (ADR-002 / Invariant L-02).
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base directories resolution
BSDD_ROOT = Path("/home/vokov/projects/b-sdd")
BSDD_DOCS_DIR = BSDD_ROOT / "docs"
BSDD_PLANS_DIR = BSDD_DOCS_DIR / "plans"

LEGAL_ROOT = Path("/home/vokov/projects/b-sdd-legal")
LEGAL_DOCS_DIR = LEGAL_ROOT / "docs"
LEGAL_PLANS_DIR = LEGAL_DOCS_DIR / "plans"

for d in (BSDD_DOCS_DIR, BSDD_PLANS_DIR, LEGAL_DOCS_DIR, LEGAL_PLANS_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_title_and_desc(content: str) -> tuple[str, str]:
    """Extracts first H1 title and first descriptive paragraph from markdown."""
    title = "Untitled Document"
    desc = ""
    lines = [line.strip() for line in content.split("\n")]
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break
        elif line.startswith("## ") and title == "Untitled Document":
            title = line.lstrip("# ").strip()

    for line in lines:
        if line and not line.startswith("#") and not line.startswith(">") and not line.startswith("```") and not line.startswith("-") and not line.startswith("["):
            desc = line[:200]
            break

    return title, desc


def _resolve_doc_path(raw_path: str, project: str = "auto") -> Optional[Path]:
    """Safely resolves document path preventing directory traversal outside allowed roots."""
    cleaned = raw_path.strip().lstrip("/")
    if ".." in cleaned:
        return None

    search_dirs: List[Path] = []
    if project == "bsdd":
        search_dirs = [BSDD_DOCS_DIR, BSDD_ROOT, LEGAL_DOCS_DIR, LEGAL_ROOT]
    elif project == "legal":
        search_dirs = [LEGAL_DOCS_DIR, LEGAL_ROOT, BSDD_DOCS_DIR, BSDD_ROOT]
    else:
        search_dirs = [BSDD_DOCS_DIR, BSDD_ROOT, LEGAL_DOCS_DIR, LEGAL_ROOT]

    # 1. Direct path
    for base in search_dirs:
        if base.exists():
            target = (base / cleaned).resolve()
            if target.is_relative_to(base) and target.exists() and target.is_file():
                return target

    # 2. Check if path starts with docs/ and strip
    if cleaned.startswith("docs/"):
        stripped = cleaned[len("docs/"):]
        for base in search_dirs:
            if base.exists():
                target = (base / stripped).resolve()
                if target.is_relative_to(base) and target.exists() and target.is_file():
                    return target

    # 3. Fuzzy match by filename
    fname = Path(cleaned).name.lower()
    for base in search_dirs:
        if base.exists():
            for p in base.rglob("*.md"):
                if p.name.lower() == fname and "node_modules" not in str(p) and ".git" not in str(p):
                    return p

    return None


def docs_list(category: Optional[str] = "all", project: Optional[str] = "all") -> Dict[str, Any]:
    """
    Lists all available system documentation, architecture specifications,
    ADRs, feedback loops, and guides.
    """
    items = []
    seen_paths = set()

    def scan_dir(base_dir: Path, proj_name: str, cat_label: str):
        if not base_dir.exists():
            return
        for p in base_dir.rglob("*.md"):
            if p.is_file() and "node_modules" not in str(p) and ".git" not in str(p):
                resolved_p = p.resolve()
                if str(resolved_p) in seen_paths:
                    continue
                seen_paths.add(str(resolved_p))

                try:
                    stat = p.stat()
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    title, desc = _extract_title_and_desc(content)

                    cat = cat_label
                    if "plans" in str(p):
                        cat = "plan"
                    elif "ADR" in str(p) or "adr" in str(p):
                        cat = "bsdd_adr"
                    elif "prompts" in str(p):
                        cat = "bsdd_prompt"
                    elif "user_guide" in str(p):
                        cat = "bsdd_user_guide"

                    items.append({
                        "filename": p.name,
                        "path": str(p),
                        "relative_path": str(p.relative_to(base_dir.parent if base_dir.name == "docs" else base_dir)),
                        "title": title,
                        "description": desc,
                        "category": cat,
                        "project": proj_name,
                        "size_bytes": stat.st_size,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    })
                except Exception:
                    pass

    # Scan BSDD docs
    if project in ("bsdd", "all", None):
        scan_dir(BSDD_DOCS_DIR, "bsdd", "bsdd_framework")
        readme_bsdd = BSDD_ROOT / "README.md"
        if readme_bsdd.exists() and str(readme_bsdd.resolve()) not in seen_paths:
            seen_paths.add(str(readme_bsdd.resolve()))
            try:
                stat = readme_bsdd.stat()
                content = readme_bsdd.read_text(encoding="utf-8", errors="ignore")
                title, desc = _extract_title_and_desc(content)
                items.append({
                    "filename": "README.md",
                    "path": str(readme_bsdd),
                    "relative_path": "README.md",
                    "title": title,
                    "description": desc,
                    "category": "system_overview",
                    "project": "bsdd",
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except Exception:
                pass

    # Scan Legal docs
    if project in ("legal", "all", None):
        scan_dir(LEGAL_DOCS_DIR, "legal", "legal_specification")
        readme_legal = LEGAL_ROOT / "README.md"
        if readme_legal.exists() and str(readme_legal.resolve()) not in seen_paths:
            seen_paths.add(str(readme_legal.resolve()))
            try:
                stat = readme_legal.stat()
                content = readme_legal.read_text(encoding="utf-8", errors="ignore")
                title, desc = _extract_title_and_desc(content)
                items.append({
                    "filename": "README.md",
                    "path": str(readme_legal),
                    "relative_path": "README.md",
                    "title": title,
                    "description": desc,
                    "category": "system_overview",
                    "project": "legal",
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                })
            except Exception:
                pass

    if category and category != "all":
        items = [i for i in items if i["category"] == category]

    return {
        "status": "ok",
        "total_documents": len(items),
        "documents": sorted(items, key=lambda x: (x["project"], x["relative_path"]))
    }


def docs_read(doc_path: str, max_chars: Optional[int] = None, project: Optional[str] = "auto") -> Dict[str, Any]:
    """
    Reads a markdown documentation or specification file by path or filename.
    """
    resolved = _resolve_doc_path(doc_path, project=project or "auto")
    if not resolved:
        return {
            "error": f"Document '{doc_path}' not found in docs directories.",
            "suggestion": "Call 'docs_list' or 'bsdd_docs_list' to view all available documents."
        }

    try:
        content = resolved.read_text(encoding="utf-8", errors="ignore")
        stat = resolved.stat()
        title, desc = _extract_title_and_desc(content)

        truncated = False
        if max_chars and len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... [TRUNCATED at {max_chars} chars, total length: {len(content)}]"
            truncated = True

        proj = "legal" if "b-sdd-legal" in str(resolved) else "bsdd"

        return {
            "status": "ok",
            "filename": resolved.name,
            "path": str(resolved),
            "project": proj,
            "title": title,
            "description": desc,
            "content": content,
            "truncated": truncated,
            "character_count": stat.st_size,
            "line_count": len(content.splitlines()),
            "word_count": len(content.split()),
            "sha256_hash": _sha256(content),
            "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": f"Failed to read '{resolved}': {str(e)}"}


def docs_write(
    doc_path: str,
    content: str,
    mode: str = "overwrite",
    author: str = "Gemini Spark Architect",
    comment: Optional[str] = None,
    project: str = "bsdd"
) -> Dict[str, Any]:
    """
    Creates or updates a documentation file in docs/.
    Guarantees path confinement inside docs/ to prevent path traversal.
    """
    cleaned = doc_path.strip().lstrip("/")
    if ".." in cleaned:
        return {"error": "Path traversal ('..') is strictly prohibited."}

    if cleaned.startswith("docs/"):
        cleaned = cleaned[len("docs/"):].lstrip("/")

    target_docs_dir = LEGAL_DOCS_DIR if project == "legal" else BSDD_DOCS_DIR
    target = (target_docs_dir / cleaned).resolve()
    if not str(target).startswith(str(target_docs_dir.resolve())):
        return {"error": f"Destination must reside within {target_docs_dir}"}

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        now_iso = datetime.now(timezone.utc).isoformat()

        if mode == "append" and target.exists():
            existing = target.read_text(encoding="utf-8", errors="ignore")
            new_content = existing + "\n\n" + f"<!-- Appended by {author} at {now_iso} -->\n" + content
            action = "appended"
        else:
            new_content = content
            action = "created" if not target.exists() else "overwritten"

        target.write_text(new_content, encoding="utf-8")
        h = _sha256(new_content)

        return {
            "status": "ok",
            "action": action,
            "filename": target.name,
            "path": str(target),
            "project": project,
            "size_bytes": len(new_content.encode("utf-8")),
            "word_count": len(new_content.split()),
            "sha256_hash": h,
            "author": author,
            "comment": comment or f"Document {action} by {author}",
            "updated_at": now_iso
        }
    except Exception as e:
        return {"error": f"Failed to write document '{doc_path}': {str(e)}"}


def plan_save(
    plan_id: str,
    title: str,
    objective: str,
    content: str,
    steps: Optional[List[str]] = None,
    status: str = "DRAFT",
    tags: Optional[List[str]] = None,
    author: str = "Gemini Spark Architect",
    project: str = "bsdd"
) -> Dict[str, Any]:
    """
    Saves a formal strategic, architectural, or procedural plan.
    Stores both structured JSON (docs/plans/{plan_id}.json) and Markdown (docs/plans/{plan_id}.md).
    """
    clean_id = re.sub(r"[^A-Za-z0-9_-]", "-", plan_id).strip("-").upper()
    if not clean_id:
        return {"error": "Invalid plan_id. Must contain alphanumeric characters, hyphens or underscores."}

    target_plans_dir = LEGAL_PLANS_DIR if project == "legal" else BSDD_PLANS_DIR
    target_plans_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_plans_dir / f"{clean_id}.json"
    md_path = target_plans_dir / f"{clean_id}.md"

    now_iso = datetime.now(timezone.utc).isoformat()
    created_at = now_iso

    if json_path.exists():
        try:
            prev = json.loads(json_path.read_text(encoding="utf-8"))
            created_at = prev.get("created_at", now_iso)
        except Exception:
            pass

    default_tags = ["b-sdd", "architecture", "spark"] if project == "bsdd" else ["b-sdd", "legal", "spark"]
    plan_payload = {
        "plan_id": clean_id,
        "title": title,
        "objective": objective,
        "status": status.upper(),
        "tags": tags or default_tags,
        "author": author,
        "project": project,
        "created_at": created_at,
        "updated_at": now_iso,
        "steps": steps or [],
        "content": content
    }

    try:
        json_path.write_text(json.dumps(plan_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        return {"error": f"Failed to save JSON plan: {e}"}

    steps_md = ""
    if steps:
        steps_md = "## Action Checklist\n" + "\n".join([f"- [ ] {step}" for step in steps]) + "\n\n"

    tags_str = ", ".join(plan_payload["tags"])
    md_content = f"""# {title}
> **Plan ID:** `{clean_id}`  
> **Status:** `{plan_payload['status']}` | **Author:** {author} | **Project:** `{project.upper()}`  
> **Created:** {created_at} | **Updated:** {now_iso}  
> **Tags:** `{tags_str}`

## Strategic Objective
{objective}

{steps_md}## Implementation Specification & Details
{content}

---
*Generated and tracked by B-SDD Sovereign Plan Registry.*
"""
    try:
        md_path.write_text(md_content, encoding="utf-8")
    except Exception as e:
        return {"error": f"Failed to save Markdown plan: {e}"}

    return {
        "status": "ok",
        "action": "plan_saved",
        "plan_id": clean_id,
        "title": title,
        "project": project,
        "plan_status": plan_payload["status"],
        "json_path": str(json_path),
        "md_path": str(md_path),
        "sha256_hash": _sha256(md_content),
        "updated_at": now_iso
    }


def plans_list(status: Optional[str] = None, tag: Optional[str] = None, project: Optional[str] = "all") -> Dict[str, Any]:
    """
    Lists all saved implementation and architectural plans in docs/plans/.
    """
    plans = []
    scanned_dirs: List[tuple[Path, str]] = []
    if project in ("bsdd", "all", None):
        scanned_dirs.append((BSDD_PLANS_DIR, "bsdd"))
    if project in ("legal", "all", None):
        scanned_dirs.append((LEGAL_PLANS_DIR, "legal"))

    seen_ids = set()
    for plans_dir, proj_name in scanned_dirs:
        if not plans_dir.exists():
            continue
        for p in plans_dir.glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                pid = data.get("plan_id", p.stem)
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)

                if status and data.get("status", "").upper() != status.upper():
                    continue
                if tag and tag.lower() not in [t.lower() for t in data.get("tags", [])]:
                    continue

                plans.append({
                    "plan_id": pid,
                    "title": data.get("title", "Untitled Plan"),
                    "objective": data.get("objective", ""),
                    "status": data.get("status", "DRAFT"),
                    "author": data.get("author", "Unknown"),
                    "project": data.get("project", proj_name),
                    "tags": data.get("tags", []),
                    "step_count": len(data.get("steps", [])),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                    "json_path": str(p),
                    "md_path": str(p.with_suffix(".md")),
                })
            except Exception:
                pass

    return {
        "status": "ok",
        "total_plans": len(plans),
        "plans": sorted(plans, key=lambda x: x.get("updated_at", ""), reverse=True)
    }


def plan_get(plan_id: str, project: Optional[str] = "auto") -> Dict[str, Any]:
    """
    Retrieves the full content and execution steps of a saved plan.
    """
    clean_id = re.sub(r"[^A-Za-z0-9_-]", "-", plan_id).strip("-").upper()

    search_dirs = []
    if project == "bsdd":
        search_dirs = [BSDD_PLANS_DIR, LEGAL_PLANS_DIR]
    elif project == "legal":
        search_dirs = [LEGAL_PLANS_DIR, BSDD_PLANS_DIR]
    else:
        search_dirs = [BSDD_PLANS_DIR, LEGAL_PLANS_DIR]

    json_path = None
    for d in search_dirs:
        if (d / f"{clean_id}.json").exists():
            json_path = d / f"{clean_id}.json"
            break

    if not json_path:
        for d in search_dirs:
            found = list(d.glob(f"*{clean_id}*.json"))
            if found:
                json_path = found[0]
                break

    if not json_path or not json_path.exists():
        return {
            "error": f"Plan '{plan_id}' not found.",
            "suggestion": "Call 'plans_list' or 'bsdd_plans_list' to view all available plans."
        }

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        return {
            "status": "ok",
            "plan": data
        }
    except Exception as e:
        return {"error": f"Failed to parse plan '{json_path}': {e}"}


def get_tools_spec(prefix: str = "legal_") -> List[Dict[str, Any]]:
    """Returns tool schemas for documentation and planning with the given prefix."""
    is_bsdd = (prefix == "bsdd_")
    proj_desc = "B-SDD system architecture" if is_bsdd else "B-SDD Legal Cockpit"
    def_proj = "bsdd" if is_bsdd else "legal"

    return [
        {
            "name": f"{prefix}docs_list",
            "description": f"Lists all {proj_desc} documentation, architecture specifications, ADRs, feedback loops, and guides available in the repository.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category: 'all', 'bsdd_framework', 'bsdd_adr', 'bsdd_methodology', 'plan', 'legal_specification', 'system_overview'.",
                        "default": "all"
                    },
                    "project": {
                        "type": "string",
                        "description": "Scope filter: 'bsdd', 'legal', or 'all'.",
                        "default": def_proj
                    }
                }
            }
        },
        {
            "name": f"{prefix}docs_read",
            "description": f"Reads full content of a documentation or specification file by path or filename (e.g. 'B_SDD_METHODOLOGY.md', 'MCP_SERVERS_AND_CAPABILITIES.md', 'README.md').",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "doc_path": {
                        "type": "string",
                        "description": "Path or filename of the document to read."
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Optional maximum characters to return to conserve tokens."
                    },
                    "project": {
                        "type": "string",
                        "description": "Project scope: 'bsdd', 'legal', or 'auto'.",
                        "default": def_proj
                    }
                },
                "required": ["doc_path"]
            }
        },
        {
            "name": f"{prefix}docs_write",
            "description": f"Creates or updates a documentation file in docs/ (e.g. 'docs/SPARK_ANALYSIS.md' or 'docs/ADR/ADR-037.md'). Securely confined to docs directory.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "doc_path": {
                        "type": "string",
                        "description": "Relative file path inside docs/ (e.g. 'SPARK_ANALYSIS.md' or 'ADR/ADR-037.md')."
                    },
                    "content": {
                        "type": "string",
                        "description": "Markdown content to write."
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["overwrite", "append"],
                        "description": "Write mode: 'overwrite' (replaces file) or 'append' (adds to end of file).",
                        "default": "overwrite"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author of this change (e.g. 'Gemini Spark Architect').",
                        "default": "Gemini Spark Architect"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Changelog note or reason for edit."
                    },
                    "project": {
                        "type": "string",
                        "enum": ["bsdd", "legal"],
                        "description": "Target project repository: 'bsdd' (/projects/b-sdd/docs) or 'legal' (/projects/b-sdd-legal/docs).",
                        "default": def_proj
                    }
                },
                "required": ["doc_path", "content"]
            }
        },
        {
            "name": f"{prefix}plan_save",
            "description": "Saves a structured strategic, architectural, or procedural plan to docs/plans/. Stores both JSON and Markdown formats for permanent tracking.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "Unique plan ID (e.g. 'PLAN-SPARK-BSDD-2026-001-CANVAS-INTEGRATION')."
                    },
                    "title": {
                        "type": "string",
                        "description": "Short concise title of the plan."
                    },
                    "objective": {
                        "type": "string",
                        "description": "Main objective and scope of the plan."
                    },
                    "content": {
                        "type": "string",
                        "description": "Full Markdown body of the plan with architecture details, decisions, and instructions."
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Actionable sequential steps or checklist."
                    },
                    "status": {
                        "type": "string",
                        "enum": ["DRAFT", "ACTIVE", "REVIEW", "APPROVED", "COMPLETED"],
                        "description": "Current lifecycle status of the plan.",
                        "default": "DRAFT"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords or tags for categorization."
                    },
                    "author": {
                        "type": "string",
                        "description": "Author (e.g. 'Gemini Spark Architect').",
                        "default": "Gemini Spark Architect"
                    },
                    "project": {
                        "type": "string",
                        "enum": ["bsdd", "legal"],
                        "description": "Target repository for plan: 'bsdd' or 'legal'.",
                        "default": def_proj
                    }
                },
                "required": ["plan_id", "title", "objective", "content"]
            }
        },
        {
            "name": f"{prefix}plans_list",
            "description": "Lists all saved implementation, strategic, and architectural plans in docs/plans/.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Optional status filter ('DRAFT', 'ACTIVE', 'APPROVED', etc.)."
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional tag filter."
                    },
                    "project": {
                        "type": "string",
                        "enum": ["bsdd", "legal", "all"],
                        "description": "Scope filter: 'bsdd', 'legal', or 'all'.",
                        "default": def_proj
                    }
                }
            }
        },
        {
            "name": f"{prefix}plan_get",
            "description": "Retrieves the full content and details of a saved plan by its plan_id.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "Unique identifier of the plan to retrieve."
                    },
                    "project": {
                        "type": "string",
                        "enum": ["bsdd", "legal", "auto"],
                        "description": "Scope filter: 'bsdd', 'legal', or 'auto'.",
                        "default": "auto"
                    }
                },
                "required": ["plan_id"]
            }
        }
    ]
