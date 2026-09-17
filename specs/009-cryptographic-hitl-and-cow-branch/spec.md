# SPEC-009: Cryptographic HITL Gate & Sovereign Git COW Branching

**Phase:** Φ1 Intent Framing  
**Status:** implemented  
**Author:** B-SDD Autonomous Systems Agent  
**Standard References:** ADR-007, ADR-011, FE-INV-03  
**Word Budget:** <500 words (ADR-002 invariant)  

---

## 1. Intent & Problem Statement
Operator decisions at Phase Φ6 (Review Gate) require mathematical and legal non-repudiation:
1. **DEF-06 (Simulated COW Branching):** Rejecting a sprint claimed to branch the project via Copy-on-Write, but returned a mock string without invoking Git (`git branch cow-branch-...`).
2. **DEF-07 (Static Ed25519 Signature):** `ReviewGateModal.tsx` hardcoded a fixed 128-character hex string rather than generating dynamic cryptographically verifiable operator tokens.
3. **INV-FE3 (Zone Fault Propagation):** Type errors within the DRAKON visual canvas crashed the parent workbench window without fault containment.

## 2. Formal Specification & Invariants
1. **ADR-007-INV-01 (WORM Isolation & Git COW Branching):**
   When an operator rejects a sprint via `POST /api/sprint/review` with `action="reject"`, the workbench server MUST execute `git branch <branch_name>` to physically isolate rejected mutations on an immutable COW branch.
2. **ADR-011-INV-01 (Cryptographic Operator Non-Repudiation):**
   `generateOperatorSignature` computes SHA-256 HMAC/Ed25519 signatures binding the operator ID, timestamp, sprint ID, and action payload.
3. **FE-INV-03 (Fault-Isolated Zone Boundaries):**
   All 4 primary workbench zones (Topbar, Visual Studio, Copilot Panel, Radar) MUST be wrapped in `AstryxZoneBoundary` error boundaries to prevent rendering cascade crashes.

## 3. Success Criteria
- [x] Physical Git branch creation verified upon sprint rejection.
- [x] WebCrypto dynamic non-repudiation signature generated and validated by Appwrite client.
- [x] Zone 2 DRAKON Canvas isolated within `AstryxZoneBoundary`.
- [x] Automated test suite `tests/test_crypto_hitl_and_cow.py` passes 100%.
