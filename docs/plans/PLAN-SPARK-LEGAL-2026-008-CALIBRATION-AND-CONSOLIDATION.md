# Sprint 008 Legal: Fact Calibration, Settings View, Kindle Pipeline & Monorepo Consolidation
> **Plan ID:** `PLAN-SPARK-LEGAL-2026-008-CALIBRATION-AND-CONSOLIDATION`  
> **Status:** `ACTIVE` | **Author:** Gemini Spark Architect | **Project:** `BSDD`  
> **Created:** 2026-09-24T15:55:56.849760+00:00 | **Updated:** 2026-09-24T15:55:56.849760+00:00  
> **Tags:** `legal, sprint_008, calibration, monorepo, kindle, utopia`

## Strategic Objective
Implement FactCalibrationModal, SettingsView, stdlib /api/v1/facts/calibrate backend, reliable Kindle dispatch, and monorepo consolidation on node .234

## Action Checklist
- [ ] Consolidate scattered modules from .161 and .184 into ~/projects/b-sdd-legal on node .234
- [ ] Run codebase dump script and upload consolidated dump to NotebookLM SSOT (c816473e-6fec-4689-90b7-98843f10bf91)
- [ ] Implement FactCalibrationModal.tsx and backend /api/v1/facts/calibrate with WORM supersession logic
- [ ] Implement SettingsView.tsx with PE24.014624-SBA parameters, Kindle email, and Appwrite OAuth hooks
- [ ] Remediate Kindle dispatch pipeline in kindle_dispatch.py and verify delivery of dossier_legal_vaud_ed10.epub
- [ ] Execute full pytest suite (100% green) and frontend build verification
- [ ] Commit to git and record WORM ledger entry

## Implementation Specification & Details
# PLAN-SPARK-LEGAL-2026-008: FACT CALIBRATION, SETTINGS VIEW & MONOREPO CONSOLIDATION

## 1. Context & Business Intent
Case PE24.014624-SBA (Ministère public du canton de Vaud).
Objective: Build a battle-tested Advocate Cockpit for Swiss/French attorneys, incorporating interactive fact calibration, dynamic blast radius recalculation, settings configuration with Appwrite OAuth readiness, and robust Send-to-Kindle book delivery.

## 2. Strict Invariants
- Invariant L-01: WORM Bitemporal Ledger (Every edit produces supersession with valid_to = NOW).
- Invariant L-02: Pure Stdlib Core Runtime (100% Python stdlib for legal core).
- Invariant L-03: Bona Fide Shield for Adriano Milli (Art. 933 CC, protégé status).
- Invariant L-04: Adult Victim Protection for Arsen Kovalenko (b. 05.11.1999, 26 ans, CPP 115/118/122).
- Invariant L-05: Cryptographic Evidence Seal (SHA-256 for all 41 items and 61 transcripts).

## 3. Actionable Checklist
1. Phase 1: Monorepo Consolidation on Node .234 (import legal_gateway.py from .161, unify pyproject/make).
2. Phase 2: Codebase Text Dump generation via b-sdd dump tool and sync to NotebookLM (c816473e-6fec-4689-90b7-98843f10bf91).
3. Phase 3: Deliverable B - Fact Calibration Modal (FactCalibrationModal.tsx) and backend endpoint /api/v1/facts/calibrate.
4. Phase 4: Deliverable A - Settings View (SettingsView.tsx) with localStorage and Appwrite connector.
5. Phase 5: Deliverable C - Advocate Action Center & fix Kindle dispatch pipeline (dossier_legal_vaud_ed10.epub -> tukroschu@kindle.com).
6. Phase 6: WORM ledger recording and n8n webhook notification.

---
*Generated and tracked by B-SDD Sovereign Plan Registry.*
