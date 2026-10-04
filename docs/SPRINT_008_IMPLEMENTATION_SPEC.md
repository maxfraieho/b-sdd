# SPRINT_008_LEGAL: INTERACTIVE CALIBRATION, SETTINGS & ADVOCATE COCKPIT IMPLEMENTATION SPECIFICATION

## 1. Metadata
- Sprint ID: sprint_008_legal
- Case Reference: Ministère public du canton de Vaud, PE24.014624-SBA
- Invariants: L-01 (WORM), L-02 (Stdlib), L-03 (Bona Fide Milli), L-04 (Adult Arsen), L-05 (ISO/IEC 27037 SHA-256)

## 2. Deliverables Summary
1. Backend: /api/v1/facts/calibrate (pure Python stdlib with WORM supersession valid_to = NOW)
2. Frontend Deliverable A: b-sdd-legal-ui/src/components/SettingsView.tsx
3. Frontend Deliverable B: b-sdd-legal-ui/src/components/FactCalibrationModal.tsx
4. Frontend Deliverable C: b-sdd-legal-ui/src/components/AdvocateActionCenter.tsx & Topbar Recompile Widget
5. Deployment: Astryx Swiss Dark theme build via npm run build and Cloudflare Pages publication.
