# SPEC-011: UI Remediation, Button Optimization & Astryx Ergonomics

* **Status:** Draft
* **Phase:** Φ1 (Intent Framing)
* **Date:** 2026-09-17
* **Author:** B-SDD Autonomous Systems & User
* **Component:** ui

## Problem Statement
The current B-SDD Developer Workbench (`b-sdd-ui`) has grown across successive feature sprints, accumulating redundant controls, visual clutter in the DRAKON palette, duplicate selectors in the Topbar, and ambiguous controls that lack intuitive feedback. An interactive remediation session with Gemini (chat and voice mode) identified key areas for decluttering, button pruning, and ergonomic consolidation according to the Swiss High-Tech Astryx design language.

## Decision Drivers & Invariants
1. **INV-011-01 (Word Budget & Invariant Density):** Specification must remain under 500 words and compile deterministically in $<50$ ms.
2. **INV-011-02 (Planar DRAKON Invariant):** The remediation pipeline flow must maintain $C=0$ (zero line crossings) with a strict vertical Happy Path skewer.
3. **INV-011-03 (No-Op Elimination):** Every visible button in the workbench must either execute a verified state action, trigger a defined modal/drawer, or be removed.
4. **INV-011-04 (Palette Ergonomics):** The default DRAKON node palette must prioritize the core planar primitive set (`action`, `question`, `ctrl-start`, `ctrl-end`, `link`), collapsing esoteric primitives into an advanced drawer.
5. **INV-011-05 (Zero Shared Crash State):** All modifications must preserve `AstryxZoneBoundary` isolation across zones A, B, C, and D.

## Target Deliverables
- Intake parser for voice audit notes (`docs/ui_remediation/remediation_input.md`).
- Cleaned Topbar eliminating redundant selectors and moving debug toggles into settings.
- Streamlined DRAKON palette focusing on 5 essential nodes.
- Automated fitness tests in `tests/test_sprint_011_ui_remediation.py` ensuring 100% pass rate.
- Automated build and Cloudflare Pages deployment verification.
