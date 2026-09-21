# ADR-009: Astryx Design System Architecture and Universal Responsive Cockpit

* **Status:** Accepted
* **Date:** 2026-09-17
* **Component:** ui
* **Supersedes:** None

## Context and Problem Statement
The developer workbench (`b-sdd-ui`) originally relied on ad-hoc Tailwind styling and lacked uniform design system primitives, causing visual inconsistency, fragile responsive layouts, and unergonomic mobile behavior. Furthermore, as documented in `docs/decision/DELTA_C_ASTRYX_OMISSION.md`, early frontend builds lacked formal Astryx component primitives and failed to provide accessible, touch-safe mobile operation for field engineers. Operator interfaces require a high-density, Swiss High-Tech Dark design system with strict accessibility, responsive ergonomics, and robust separation between desktop multi-zone views and mobile execution cockpits.

## Decision Drivers
* Standardize on the Astryx component architecture (`Button`, `IconButton`, `Badge`, `Dot`, `Banner`, `Selector`, `Segmented`, `Dialog`, `Drawer`, `Toast`).
* Enforce the Swiss High-Tech Dark design language (dark canvas `#090d13`, panel `#0d121c`, card `#141b27`, amber and emerald semantic accents).
* Provide full responsive parity between desktop wide screens and mobile touchscreen devices.
* Guarantee touch-safe ergonomic interaction for DRAKON logic modeling and HITL Phase reviews.
* Maintain universal portability and zero runtime regression in client bundles.

## Considered Options
1. Retain ad-hoc Tailwind classes with no unified component contracts (High visual fragmentation, broken mobile experience).
2. Heavy third-party proprietary component libraries requiring cloud telemetry or conflicting CSS runtimes.
3. Astryx Design System architecture with Swiss High-Tech Dark CSS custom properties, typed primitives, and dual responsive cockpits (Desktop & Mobile) (Chosen).

## Decision Outcome
Chosen option: **Astryx Design System Architecture and Universal Responsive Cockpit** (Option 3).

### 1. Astryx Primitives Layer
The UI standardizes on accessible Astryx primitives in `src/components/astryx/`:
* `Button` / `IconButton`: Strict variant contracts (`primary`, `secondary`, `success`, `destructive`, `ghost`) and sizing (`sm`, `md`, `lg`).
* `Badge` / `Dot`: Status indicators supporting `emerald`, `amber`, `cyan`, `rose`, `violet`, and pulsing states.
* `Banner`: Contextual invariant feedback with action slots.
* `Selector`: Stylized bound selection for specifications, projects, and pipeline templates.
* `Segmented`: Keyboard-navigable multi-state mode switches.
* `Dialog` / `Drawer`: High-density modal flows and sliding side drawers.
* `Toast`: Ephemeral notification queue for synchronous server operations.

### 2. Dual Responsive Cockpit Modes
The workbench provides two synchronized view modes:
* **Desktop Cockpit (>=768px):** Full 4-zone high-density view (Topbar, HITL Stepper, DRAKON Studio, LLM Copilot panel, Bitemporal Radar strip).
* **Mobile Cockpit (<768px or explicit toggle):** Touch-friendly single-view interface with bottom navigation tabs (`ДРАКОН`, `Копілот`, `Радар`, `Фази`) and touch-safe vertical workflow visualization.
* **Manual Override:** Operators can explicitly toggle between Desktop and Mobile preview modes at any time.

## Invariants
- ADR-009-INV-01: Operator cockpit UI must strictly compose Astryx-shaped primitives adhering to the Swiss High-Tech Dark design specification.
- ADR-009-INV-02: Operator cockpit must support dual responsive rendering (Desktop Multi-Zone & Mobile Ergonomic) with explicit user-controllable preview toggles.
- ADR-009-INV-03: Mobile view must provide touch-safe vertical workflow visualization and prevent mouse-dependent CAD drag locks on mobile touchscreens.
