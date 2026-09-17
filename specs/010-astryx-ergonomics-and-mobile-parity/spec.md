# SPEC-010: Astryx Design System Ergonomics & Responsive Mobile Parity

**Phase:** Φ1 Intent Framing  
**Status:** implemented  
**Author:** B-SDD Autonomous Systems Agent  
**Standard References:** ADR-002, ADR-009, ADR-FE-001, FE-INV-01, FE-INV-02  
**Word Budget:** <500 words (ADR-002 invariant)  

---

## 1. Intent & Problem Statement
Four ergonomic and layout defects degrade the Swiss High-Tech Dark design system compliance:
1. **DEF-04 (Lost Mobile Nav ADR Callback):** `MobileNavigation.tsx` dropped the `onOpenAdrLibrary` prop, locking mobile users out of the ADR library.
2. **INV-T1 (Word vs Token Semantics):** `TokenGauge.tsx` mislabeled the ADR-002 strict word budget (<500 words) as tokens.
3. **INV-FE1 (Double Body Scroll):** Missing `min-width: 0` constraints and explicit flex overflow caused horizontal/vertical canvas bleed.
4. **INV-AST (Residual Hardcoded Colors):** Hardcoded hex color codes (`#0d121c`, `#1e293b`, `#141b27`, `#090d13`) breached the Astryx CSS custom property palette.

## 2. Formal Specification & Invariants
1. **FE-INV-01 (100vh No-Body-Scroll Cockpit):**
   The application root and main container MUST maintain strict viewport clamping (`h-screen overflow-hidden`) with zero global page scrolling.
2. **FE-INV-02 (Pure Astryx Semantic Palette):**
   All component surfaces, borders, and text MUST bind to CSS custom properties (`bg-canvas`, `bg-panel`, `bg-card`, `border-border-subtle`, `text-amber`, `text-cyan`).
3. **ADR-002-INV-01 (Strict Word Budget Alignment):**
   `TokenGauge.tsx` displays the exact word count alongside estimated token equivalence, clearly communicating the $\le 500$ word pre-flight limit.
4. **ADR-FE-001 (100% Mobile Architectural Parity):**
   `MobileNavigation.tsx` MUST provide direct touch access to the ADR Library, Task Backlog, and Invariant Inspector.

## 3. Success Criteria
- [x] `onOpenAdrLibrary` button rendered in `MobileNavigation.tsx`.
- [x] `TokenGauge.tsx` migrated to semantic Astryx classes with word/token distinction.
- [x] Zero hardcoded hex colors in `MobileNavigation.tsx` and `TokenGauge.tsx`.
- [x] Production build `npm run build` succeeds cleanly.
- [x] Automated test suite `tests/test_astryx_ergonomics_and_mobile.py` passes 100%.
