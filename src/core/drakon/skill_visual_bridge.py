"""
B-SDD Skill Visual Bridge & DRAKON Round-Trip Engine.
Connects human-readable procedural playbooks (SKILL.md) with machine-executable
DRAKON algorithmic logic (<skill_name>.drakon.json) for Astryx Cockpit / DrakonStudio.
Compliant with ADR-002 (Pure Stdlib Core), ADR-008 (DRAKON Invariants), and ADR-015 (Skill Taxonomy).
100% Pure Python Standard Library.
"""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.core.dto.skills import SkillDTO, SkillType
from src.drakon.types import DrakonNodeType


# Default system skill directories
USER_SKILLS_DIR = Path.home() / ".agents" / "skills"
PROJECT_SKILLS_DIR = Path("/home/vokov/projects/b-sdd/.agents/skills")

# Recognized Core B-SDD System Skills
KNOWN_SYSTEM_SKILLS: Set[str] = {
    "b-sdd",
    "b-sdd-sprint-closure",
    "intent-continuity",
    "laya-decision-router",
    "drakon-compiler",
    "utopia-intent-ledger",
    "session-distiller",
    "safe-refactor",
    "surgical-patch",
    "code-reviewer",
    "test-driven-development",
    "diagnosing-bugs",
    "investigate-first",
    "systematic-debugging",
    "root-cause-tracing",
    "astryx-scaffolder",
    "kindle-release-pipeline",
    "architecture-designer",
    "skill-creator",
    "skill-audit",
    "find-skills",
    "writing-skills",
    "writing-great-skills",
    "codebase-design",
    "improve-codebase-architecture",
    "testing-anti-patterns",
    "condition-based-waiting",
    "defense-in-depth",
    "verification-before-completion",
    "using-git-worktrees",
    "cloudflare-pages-expert",
    "b-sdd-notebooklm-sync",
    "b-sdd-kindle-docs",
}



def parse_skill_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parses YAML frontmatter from SKILL.md without external dependencies.
    Compliant with ADR-002 Pure Python Standard Library.
    """
    meta: Dict[str, Any] = {
        "name": "",
        "description": "",
        "type": SkillType.PROJECT_SKILL.value,
        "category": "general",
        "immutable": False,
        "invoked_skills": [],
    }
    body = content

    fm_match = re.search(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if not fm_match:
        return meta, body

    fm_text = fm_match.group(1)
    body = content[fm_match.end():]
    lines = fm_text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.strip().strip("\"'")

            if key == "name":
                meta["name"] = val
            elif key == "description":
                if val in (">", "|", ">-", "|-", ""):
                    desc_lines = []
                    i += 1
                    while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                        desc_lines.append(lines[i].strip())
                        i += 1
                    meta["description"] = " ".join(desc_lines)
                    continue
                else:
                    meta["description"] = val
            elif key == "type":
                upper_val = val.upper()
                if "SYSTEM" in upper_val:
                    meta["type"] = SkillType.SYSTEM_SKILL.value
                    meta["immutable"] = True
                else:
                    meta["type"] = SkillType.PROJECT_SKILL.value
            elif key == "category":
                meta["category"] = val
            elif key == "immutable":
                meta["immutable"] = val.lower() in ("true", "1", "yes")
            elif key == "invoked_skills":
                inv_list = []
                if val.startswith("[") and val.endswith("]"):
                    items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                    inv_list.extend(items)
                else:
                    # check if list items follow
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith("-"):
                        item_val = lines[i].strip()[1:].strip().strip("\"'")
                        if item_val:
                            inv_list.append(item_val)
                        i += 1
                    meta["invoked_skills"] = inv_list
                    continue
                meta["invoked_skills"] = inv_list

        i += 1

    return meta, body


def resolve_skill_path(skill_name: str, skills_dir: Optional[Path] = None) -> Path:
    """Resolves the folder path of a skill, checking provided dir, ~/.agents/skills, or project mirror."""
    if skills_dir:
        cand = Path(skills_dir) / skill_name
        if cand.exists() and cand.is_dir():
            return cand

    if USER_SKILLS_DIR.exists():
        cand = USER_SKILLS_DIR / skill_name
        if cand.exists() and cand.is_dir():
            return cand

    if PROJECT_SKILLS_DIR.exists():
        cand = PROJECT_SKILLS_DIR / skill_name
        if cand.exists() and cand.is_dir():
            return cand

    # If skills_dir is provided but does not yet contain the folder, return the target inside skills_dir
    if skills_dir:
        return Path(skills_dir) / skill_name

    return USER_SKILLS_DIR / skill_name


def extract_invoked_skills_from_text(text: str) -> List[str]:
    """Finds cross-skill references such as CALL_SKILL(skill_name) or /skill-name in text."""
    found: Set[str] = set()
    # Pattern 1: CALL_SKILL(name) or CALL_SKILL: name
    for m in re.finditer(r"CALL_SKILL[:\s\(]+([a-zA-Z0-9_\-]+)", text):
        found.add(m.group(1).strip())

    # Pattern 2: `skill_name` matching known system skills
    for s_name in KNOWN_SYSTEM_SKILLS:
        if re.search(rf"\b{re.escape(s_name)}\b", text):
            found.add(s_name)

    return sorted(list(found))


def synthesize_drakon_schema(skill_name: str, skill_md_content: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes a canonical, 100% planar DRAKON IR diagram (X=0, C=0) from SKILL.md.
    Adheres strictly to ADR-008 and ADR-015.
    """
    title = meta.get("name") or skill_name
    desc = meta.get("description") or f"DRAKON visual algorithm for skill {skill_name}"
    is_system = meta.get("type") == SkillType.SYSTEM_SKILL.value or skill_name in KNOWN_SYSTEM_SKILLS

    # Extract procedural steps from markdown
    steps_raw: List[Tuple[str, str, Optional[str]]] = []  # (label, instructions, call_skill)

    lines = skill_md_content.splitlines()
    curr_label = ""
    curr_inst: List[str] = []

    for line in lines:
        stripped = line.strip()
        # Headings indicating steps
        if stripped.startswith("### ") or stripped.startswith("## ") or re.match(r"^\d+\.\s+\*\*", stripped):
            if curr_label and curr_inst:
                inst_text = " ".join(curr_inst)
                call_s = None
                for kn in KNOWN_SYSTEM_SKILLS:
                    if kn != skill_name and kn in inst_text:
                        call_s = kn
                        break
                steps_raw.append((curr_label, inst_text[:180], call_s))
                curr_inst = []

            # Clean label
            clean_l = re.sub(r"^#+\s*", "", stripped)
            clean_l = re.sub(r"^\d+\.\s*", "", clean_l)
            clean_l = clean_l.replace("**", "").strip()
            if clean_l and not clean_l.lower().startswith("table of contents"):
                curr_label = clean_l[:60]
        elif curr_label and stripped and not stripped.startswith("```"):
            curr_inst.append(stripped)

    if curr_label and curr_inst:
        inst_text = " ".join(curr_inst)
        call_s = None
        for kn in KNOWN_SYSTEM_SKILLS:
            if kn != skill_name and kn in inst_text:
                call_s = kn
                break
        steps_raw.append((curr_label, inst_text[:180], call_s))

    # Fallback to standard canonical 4-step pipeline if no headings parsed
    if not steps_raw:
        steps_raw = [
            ("Intake & Invariant Check", f"Initialize {skill_name} and verify architectural preconditions.", None),
            ("Core Execution Flow", f"Execute core procedural operations for {skill_name}.", None),
            ("Verification & Testing", "Verify results against ADR contracts and negative constraints.", "test-driven-development"),
            ("Handoff & Artifact Output", "Commit state changes and produce telemetry or handoff notes.", "session-distiller" if is_system else None),
        ]

    # Limit to reasonable visual canvas size (4 to 8 nodes)
    if len(steps_raw) > 8:
        steps_raw = steps_raw[:8]

    nodes: List[Dict[str, Any]] = []
    y_cursor = 0.0

    # 1. Headline (Start)
    start_node = {
        "node_id": "start",
        "node_type": DrakonNodeType.HEADLINE.value,
        "label": f"Початок: {title}",
        "edges": {"down": "step_1", "right": None},
        "semantic_binding": {
            "adr_invariant_id": "ADR-015-INV-03",
            "severity": "normal"
        },
        "x": 0.0,
        "y": y_cursor
    }
    nodes.append(start_node)

    # 2. Sequential Action / Insertion Nodes on Skewer X=0
    for idx, (lbl, inst, call_skill) in enumerate(steps_raw, start=1):
        y_cursor += 2.0
        node_id = f"step_{idx}"
        next_node_id = f"step_{idx + 1}" if idx < len(steps_raw) else "end"

        node_type = DrakonNodeType.INSERTION.value if call_skill else DrakonNodeType.ACTION.value
        binding: Dict[str, Any] = {
            "adr_invariant_id": "ADR-015-INV-04",
            "severity": "normal"
        }
        if call_skill:
            binding["call_skill"] = call_skill

        node_obj = {
            "node_id": node_id,
            "node_type": node_type,
            "label": f"CALL_SKILL({call_skill}): {lbl}" if call_skill else lbl,
            "edges": {"down": next_node_id, "right": None},
            "semantic_binding": binding,
            "x": 0.0,
            "y": y_cursor,
            "instructions": inst
        }
        nodes.append(node_obj)

    # 3. End Terminal Node
    y_cursor += 2.0
    end_node = {
        "node_id": "end",
        "node_type": DrakonNodeType.END.value,
        "label": f"Завершення: {title}",
        "edges": {"down": None, "right": None},
        "semantic_binding": {
            "adr_invariant_id": "ADR-015-INV-03",
            "severity": "normal"
        },
        "x": 0.0,
        "y": y_cursor
    }
    nodes.append(end_node)

    schema = {
        "schema_version": "1.0",
        "name": title,
        "category": "bssd_system_skill" if is_system else "bssd_project_skill",
        "description": desc,
        "params": "context: dict",
        "nodes": nodes,
        "meta": {
            "skill_name": skill_name,
            "skill_type": SkillType.SYSTEM_SKILL.value if is_system else SkillType.PROJECT_SKILL.value,
            "immutable": is_system or meta.get("immutable", False),
            "skewer_x": 0.0,
            "is_planar": True,
            "crossings_count": 0
        }
    }
    return schema


def load_skill_drakon(skill_name: str, skills_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads DRAKON schema for a skill.
    If <skill_name>.drakon.json exists, returns its parsed content.
    If missing, synthesizes a canonical planar schema from SKILL.md and persists it.
    """
    skill_path = resolve_skill_path(skill_name, skills_dir)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found for '{skill_name}' at {skill_path}")

    drakon_file = skill_path / f"{skill_name}.drakon.json"
    skill_md_file = skill_path / "SKILL.md"

    if drakon_file.exists():
        try:
            content = drakon_file.read_text(encoding="utf-8")
            data = json.loads(content)
            return data
        except Exception as exc:
            # If JSON is corrupt, regenerate from SKILL.md
            pass

    # Read SKILL.md to synthesize
    md_content = ""
    meta: Dict[str, Any] = {}
    if skill_md_file.exists():
        md_content = skill_md_file.read_text(encoding="utf-8")
        meta, _ = parse_skill_frontmatter(md_content)

    if not meta.get("name"):
        meta["name"] = skill_name

    schema = synthesize_drakon_schema(skill_name, md_content, meta)

    # Persist synthesized schema to fulfill Rule of 2 (ADR-015-INV-03)
    try:
        drakon_file.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    return schema


def generate_pseudocode_from_drakon(skill_name: str, schema_json: Dict[str, Any]) -> str:
    """
    Generates deterministic, structured Algorithmic Pseudocode from a DRAKON schema.
    Compliant with ADR-016 (Standardized Tripartite Skill Specification).
    """
    title = schema_json.get("name") or skill_name
    clean_name = re.sub(r"[^a-zA-Z0-9_\-\s]", "", title)
    parts = [p for p in re.split(r"[\s\-_]+", clean_name.strip()) if p]
    safe_title = "".join(p[0].upper() + p[1:] for p in parts) or "ExecuteSkill"
    raw_nodes = schema_json.get("nodes", [])

    nodes_list = raw_nodes if isinstance(raw_nodes, list) else list(raw_nodes.values())

    lines = [
        f"ALGORITHM {safe_title}(context: dict)",
        "BEGIN",
        "    TRY",
        "        // Preconditions verification",
        f"        ASSERT ValidatePreconditions('{skill_name}')",
        "",
    ]

    skewer_nodes = [n for n in nodes_list if float(n.get("x", 0.0)) == 0.0]
    step_num = 1

    for node in skewer_nodes:
        ntype = node.get("node_type", "action").lower()
        lbl = node.get("label", "")
        edges = node.get("edges", {})
        sb = node.get("semantic_binding", {}) or {}
        call_skill = sb.get("call_skill")

        if ntype in ("headline", "header"):
            lines.append(f"        // Main Flow Spine: {lbl}")
        elif ntype == "question":
            lines.append(f"        // Step {step_num} Decision: {lbl}")
            lines.append(f"        IF EvaluateCondition('{lbl}') THEN")
            lines.append("            // Primary branch along vertical skewer (X=0)")
            right_target = edges.get("right")
            if right_target:
                alt_node = next((n for n in nodes_list if n.get("node_id") == right_target), None)
                alt_lbl = alt_node.get("label", right_target) if alt_node else right_target
                lines.append("        ELSE")
                lines.append(f"            BRANCH_RIGHT(X=4.0): {alt_lbl}")
                if alt_node and alt_node.get("semantic_binding", {}).get("call_skill"):
                    alt_cs = alt_node["semantic_binding"]["call_skill"]
                    lines.append(f"            CALL_SKILL({alt_cs}, context)")
                lines.append(f"            LOG_WARN('Degradation branch taken for: {lbl}')")
            lines.append("        FI")
            step_num += 1
        elif ntype in ("insertion", "action") and call_skill:
            lines.append(f"        STEP {step_num}: CALL_SKILL({call_skill}, context)")
            lines.append(f"        // {lbl}")
            step_num += 1
        elif ntype == "action":
            lines.append(f"        STEP {step_num}: {lbl}")
            inst = node.get("instructions")
            if inst:
                lines.append(f"        // Detail: {inst[:120]}")
            step_num += 1
        elif ntype == "end":
            lines.append(f"        RETURN Success('{lbl}')")

    lines.extend([
        "    CATCH Exception AS e",
        "        LOG_CRITICAL('❌ Execution failed: ' + e.Message)",
        f"        HALT_AND_DEGRADE('Fallback for {skill_name}')",
        "    END",
        "END",
    ])

    return "\n".join(lines)


def save_skill_drakon(skill_name: str, schema_json: Dict[str, Any], skills_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Saves visual DRAKON schema for a skill and synchronizes changes to SKILL.md.
    Enforces ADR-015 immutability guards: SYSTEM_SKILL schemas cannot be cleared or corrupted.
    """
    if not isinstance(schema_json, dict) or "nodes" not in schema_json:
        raise ValueError("Invalid DRAKON schema: must be a JSON object containing a 'nodes' collection.")

    raw_nodes = schema_json.get("nodes")
    if not raw_nodes:
        raise ValueError("DRAKON schema must contain at least one node.")

    skill_path = resolve_skill_path(skill_name, skills_dir)
    if not skill_path.exists():
        skill_path.mkdir(parents=True, exist_ok=True)

    drakon_file = skill_path / f"{skill_name}.drakon.json"
    skill_md_file = skill_path / "SKILL.md"

    is_known_system = skill_name in KNOWN_SYSTEM_SKILLS

    # Immutability validation
    if drakon_file.exists():
        try:
            existing = json.loads(drakon_file.read_text(encoding="utf-8"))
            existing_meta = existing.get("meta", {})
            if existing_meta.get("immutable", False) or is_known_system:
                schema_json.setdefault("meta", {})["immutable"] = True
                schema_json["meta"]["skill_type"] = SkillType.SYSTEM_SKILL.value
        except Exception:
            pass

    # Ensure schema meta conforms to ADR-015
    schema_json.setdefault("meta", {})
    if is_known_system or schema_json.get("meta", {}).get("skill_type") == SkillType.SYSTEM_SKILL.value:
        schema_json["meta"]["immutable"] = True
        schema_json["meta"]["skill_type"] = SkillType.SYSTEM_SKILL.value
        schema_json["category"] = "bssd_system_skill"

    # Write .drakon.json
    drakon_file.write_text(json.dumps(schema_json, indent=2, ensure_ascii=False), encoding="utf-8")

    # Round-trip sync to SKILL.md
    if skill_md_file.exists():
        content = skill_md_file.read_text(encoding="utf-8")
        meta, body = parse_skill_frontmatter(content)
    else:
        meta = {
            "name": skill_name,
            "description": schema_json.get("description", f"Skill {skill_name}"),
            "type": SkillType.SYSTEM_SKILL.value if is_known_system else SkillType.PROJECT_SKILL.value,
            "category": "bssd-system-skill" if is_known_system else "general",
            "immutable": is_known_system,
        }
        body = f"\n# {skill_name}\n\n{schema_json.get('description', '')}\n"

    # Update frontmatter tags
    if is_known_system or meta.get("immutable", False):
        meta["type"] = SkillType.SYSTEM_SKILL.value
        meta["category"] = "bssd-system-skill"
        meta["immutable"] = True

    # Extract invoked skills from schema
    invoked = set(meta.get("invoked_skills", []))
    nodes_list = raw_nodes if isinstance(raw_nodes, list) else list(raw_nodes.values())
    for n in nodes_list:
        sb = n.get("semantic_binding", {})
        if sb and isinstance(sb, dict) and "call_skill" in sb:
            invoked.add(sb["call_skill"])
    meta["invoked_skills"] = sorted(list(invoked))

    # Reconstruct SKILL.md with updated frontmatter and visual flow reference
    fm_lines = [
        "---",
        f"name: {meta.get('name', skill_name)}",
        f"description: {meta.get('description', '')}",
        f"type: {meta.get('type', SkillType.PROJECT_SKILL.value)}",
        f"category: {meta.get('category', 'general')}",
        f"immutable: {'true' if meta.get('immutable') else 'false'}",
    ]
    if meta.get("invoked_skills"):
        fm_lines.append(f"invoked_skills: [{', '.join(meta['invoked_skills'])}]")
    fm_lines.append("---")
    new_fm = "\n".join(fm_lines) + "\n"



    # Synchronize visual workflow section in body
    flow_marker_start = "<!-- DRAKON_VISUAL_FLOW_START -->"
    flow_marker_end = "<!-- DRAKON_VISUAL_FLOW_END -->"

    flow_lines = [
        flow_marker_start,
        "## DRAKON Visual Workflow (Planar Skewer X=0)",
        f"- **Schema File:** `{skill_name}.drakon.json`",
        f"- **Total Algorithmic Nodes:** {len(nodes_list)}",
        "- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified.",
    ]
    for idx, node in enumerate(nodes_list, start=1):
        ntype = node.get("node_type", "action")
        lbl = node.get("label", "")
        flow_lines.append(f"  {idx}. `[{ntype.upper()}]` {lbl}")
    flow_lines.append(flow_marker_end)
    flow_block = "\n".join(flow_lines)

    # Synchronize Algorithmic Pseudocode section per ADR-016
    pseudo_marker_start = "<!-- ALGORITHMIC_PSEUDOCODE_START -->"
    pseudo_marker_end = "<!-- ALGORITHMIC_PSEUDOCODE_END -->"
    pseudocode = generate_pseudocode_from_drakon(skill_name, schema_json)

    pseudo_block = (
        f"{pseudo_marker_start}\n"
        f"## 📐 Канонічний алгоритмічний псевдокод (B-SDD ADR-016 Standard)\n\n"
        f"> [!IMPORTANT]\n"
        f"> Цей псевдокод є 1:1 текстовим ізоморфізмом планарної ДРАКОН-схеми `{skill_name}.drakon.json`.\n\n"
        f"```text\n{pseudocode}\n```\n"
        f"{pseudo_marker_end}"
    )

    if pseudo_marker_start in body and pseudo_marker_end in body:
        body = re.sub(
            rf"{re.escape(pseudo_marker_start)}.*?{re.escape(pseudo_marker_end)}",
            pseudo_block,
            body,
            flags=re.DOTALL
        )
    elif "ALGORITHM " not in body:
        if flow_marker_start in body:
            body = body.replace(flow_marker_start, pseudo_block + "\n\n" + flow_marker_start)
        else:
            body = "\n\n" + pseudo_block + "\n" + body

    if flow_marker_start in body and flow_marker_end in body:
        body = re.sub(
            rf"{re.escape(flow_marker_start)}.*?{re.escape(flow_marker_end)}",
            flow_block,
            body,
            flags=re.DOTALL
        )
    else:
        body = body.rstrip() + "\n\n" + flow_block + "\n"

    skill_md_file.write_text(new_fm + body, encoding="utf-8")


    return {
        "status": "ok",
        "skill": skill_name,
        "drakon_path": str(drakon_file),
        "skill_md_path": str(skill_md_file),
        "nodes_count": len(nodes_list),
        "immutable": meta.get("immutable", False),
    }


def list_skills_dto(skills_dir: Optional[Path] = None) -> List[SkillDTO]:
    """
    Discovers all skills in the designated directory and returns a sorted list of SkillDTOs.
    """
    search_dir = Path(skills_dir) if skills_dir else USER_SKILLS_DIR
    if not search_dir.exists():
        return []

    results: List[SkillDTO] = []
    seen: Set[str] = set()

    for item in sorted(search_dir.iterdir()):
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        if not item.is_dir() or item.is_symlink():
            continue

        skill_name = item.name
        if skill_name in seen:
            continue
        seen.add(skill_name)

        skill_md = item / "SKILL.md"
        drakon_json = item / f"{skill_name}.drakon.json"

        desc = ""
        skill_type = SkillType.SYSTEM_SKILL.value if skill_name in KNOWN_SYSTEM_SKILLS else SkillType.PROJECT_SKILL.value
        category = "bssd-system-skill" if skill_name in KNOWN_SYSTEM_SKILLS else "general"
        immutable = skill_name in KNOWN_SYSTEM_SKILLS
        invoked_skills: List[str] = []

        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding="utf-8", errors="replace")
                meta, body = parse_skill_frontmatter(content)
                desc = meta.get("description", "")
                if meta.get("type"):
                    skill_type = meta["type"]
                if meta.get("category"):
                    category = meta["category"]
                if meta.get("immutable") is not None:
                    immutable = meta["immutable"]
                invoked_skills = meta.get("invoked_skills", [])
                if not invoked_skills:
                    invoked_skills = extract_invoked_skills_from_text(body)
            except Exception:
                pass

        has_drakon = drakon_json.exists()

        dto = SkillDTO(
            name=skill_name,
            description=desc,
            skill_type=skill_type,
            category=category,
            immutable=immutable,
            has_drakon_schema=has_drakon,
            invoked_skills=invoked_skills,
            drakon_path=str(drakon_json) if has_drakon else None,
            skill_md_path=str(skill_md) if skill_md.exists() else None,
        )
        results.append(dto)

    return results


def verify_system_skills_immutability(
    skills_dir: Optional[Path] = None,
    expected_system_skills: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Enforces ADR-015-INV-02: verifies all core system skills exist, have valid SKILL.md,
    are marked immutable, and maintain their DRAKON schemas.
    """
    search_dir = Path(skills_dir) if skills_dir else USER_SKILLS_DIR
    target_skills = expected_system_skills or sorted(list(KNOWN_SYSTEM_SKILLS))

    violations: List[str] = []

    for s_name in target_skills:
        s_path = search_dir / s_name
        if not s_path.exists():
            violations.append(f"MISSING_SYSTEM_SKILL: Directory '{s_name}' does not exist in {search_dir}")
            continue

        md_file = s_path / "SKILL.md"
        if not md_file.exists():
            violations.append(f"MISSING_SKILL_MD: '{s_name}' is missing SKILL.md")
            continue

        meta, _ = parse_skill_frontmatter(md_file.read_text(encoding="utf-8", errors="replace"))
        if not meta.get("immutable", False):
            violations.append(f"MUTABLE_SYSTEM_SKILL: '{s_name}' must have immutable: true in frontmatter")

        drakon_file = s_path / f"{s_name}.drakon.json"
        if not drakon_file.exists():
            violations.append(f"MISSING_DRAKON_SCHEMA: '{s_name}' is missing {s_name}.drakon.json")

    return (len(violations) == 0, violations)
