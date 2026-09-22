---
name: b-sdd
description: Enforces bitemporal architectural invariants, ADR compliance, and pre-flight compilation under the B-SDD framework.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [architecture-designer, skill-creator]
---
# B-SDD (Bitemporal Spec-Driven Development) Agent Skill

When operating in any repository governed by the **B-SDD Framework**, you MUST follow this operational protocol:

## 1. Pre-Flight Phase (Always First)
Before planning or writing code:
1. Ensure `.context/active_rules.md` is compiled. If starting fresh, invoke `./run_agy.sh` or run:
   ```bash
   python3 -m src.cli.main compile
   ```
2. Read `.context/active_rules.md`. These are **MANDATORY ARCHITECTURAL INVARIANTS**. You must never violate or bypass them.
3. Check the `RECOMMENDED PROCEDURAL SKILLS` section at the bottom of `.context/active_rules.md`.
   - If a recommended skill matches your task (e.g. `architecture-designer`, `safe-refactor`), activate and follow its playbook.
   - If a needed capability is absent, invoke `find-skills` to locate it.

## 2. Decision & Supersession Protocol (Changing Architecture)
When introducing a new architecture pattern or retiring an old one:
1. Do NOT delete old ADRs or leave conflicting rules in the repo.
2. Create a new ADR using the CLI or template:
   ```bash
   python3 -m src.cli.main adr new "Your Decision Title" --component <domain> --supersedes ADR-XXX
   ```
3. Ensure the new ADR contains a `## Invariants` section and explicit `* **Supersedes:** ADR-XXX`.
4. Synchronize with Utopia DB:
   ```bash
   python3 -m src.cli.main sync
   ```
   This atomically marks the old decision as `superseded` (`valid_to = NOW`) and prevents any agent from resurrecting deprecated patterns.

## 3. The Rule of 2 (Autonomous Skill Crystallization)
If you observe or execute an operational sequence, diagnostic workflow, or API integration that repeats **$\ge 2$ times** without a standardized agent skill:
- Stop and propose creating a permanent skill.
- Use `skill-creator` to scaffold and test `.agents/skills/<new-skill>/SKILL.md`.

## 4. Verification Gate (Before Any Commit)
Before committing or completing a task:
1. Run the automated architecture fitness suite:
   ```bash
   pytest -v tests/test_architecture_fitness.py
   ```
2. Ensure all 5 criteria pass:
   - Compile latency < 50ms.
   - Context word count < 500 words.
   - Zero external third-party dependencies in `src/`.
   - Supersession DAG integrity verified.
   - Procedural skill recommendations verified.

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `b-sdd.drakon.json`
- **Total Algorithmic Nodes:** 6
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified.
  1. `[HEADLINE]` Початок: b-sdd
  2. `[INSERTION]` CALL_SKILL(architecture-designer): Pre-Flight Phase (Always First)
  3. `[ACTION]` Decision & Supersession Protocol (Changing Architecture)
  4. `[INSERTION]` CALL_SKILL(skill-creator): The Rule of 2 (Autonomous Skill Crystallization)
  5. `[ACTION]` Verification Gate (Before Any Commit)
  6. `[END]` Завершення: b-sdd
<!-- DRAKON_VISUAL_FLOW_END -->
