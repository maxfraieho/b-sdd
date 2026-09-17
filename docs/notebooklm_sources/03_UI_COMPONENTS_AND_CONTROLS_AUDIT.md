# B-SDD WORKBENCH UI ARCHITECTURE, COMPONENT CATALOG & INTERACTIVE CONTROLS AUDIT

**Target System:** `b-sdd-ui` (React 19 + TypeScript + Tailwind CSS + Astryx Primitives + DrakonWidget)  
**Corpus / Context:** B-SDD Methodology, Multi-Session Handoff & Architecture  
**Audit Purpose:** Identify all architectural defects, user interface discrepancies, dead buttons ('кнопки, що нічого не дають'), mock data traps, and cross-subsystem synchronization gaps.

---

## 1. Executive Summary & Critical Findings

A systematic audit was conducted on all 25 React components, custom hooks, and API bridges in the `b-sdd-ui` codebase and its Python backend `workbench_server.py`. 

### Key Categories of Identified Problems:
1. **Dead Controls & Missing Bindings (Zero Effect on Click)**:
   - Several UI buttons, icons, or menu items trigger no state transition, invoke undefined props, or load empty data arrays.
2. **Mock Traps & Simulation Disconnects**:
   - Critical governance actions (such as Copy-On-Write branch creation, Ed25519 cryptographic signing, and Copilot LLM generation) operate on static canned mocks without delegating to their designated sovereign backends (Git, WebCrypto, LLM Gateway `192.168.3.184:18880`).
3. **Visual vs. State Drift (Dual Representation Trap)**:
   - Two separate models exist for DRAKON diagrams: visual nodes in `drakonwidget.js` canvas and React state `drakonNodes` in `App.tsx`. Visual edits on the canvas do not propagate to `drakonNodes`, causing pseudocode generation and backend saves to emit outdated or empty graphs.
4. **Cloudflare Pages / Production Deployment Disconnect (Mixed Content Barrier)**:
   - When deployed on HTTPS (`https://b-sdd-ui.pages.dev`), the frontend attempts to contact `http://localhost:8765`. Modern browsers block mixed HTTP active content, and remote devices (e.g. mobile phones) do not run a local Python server on port 8765. This causes the UI to permanently freeze in fallback mock mode.
5. **Architectural Invariant Discrepancies**:
   - ADR-002 enforces a strict raw word budget (<500 words), while the UI token gauge displays estimated tokens (word_count * 1.35) and titles it as a token budget, creating cognitive dissonance for operators.
   - Bitemporal scrubbing is artificially constrained to 16 calendar days in September 2026 rather than binding dynamically to the repository git commit log and Utopia DB transaction ledger.

---

## 2. Complete Inventory of All 25 UI Components

| # | Component | File Path | Functional Responsibility |
|---|---|---|---|
| 1 | `App` | `src/App.tsx` | Root orchestration, state management, live hooks, modal controllers |
| 2 | `Topbar` | `src/components/Topbar.tsx` | Zone 1 header, project selector, spec dropdown, sovereign node health chips, telemetry badge |
| 3 | `PhaseStepper` | `src/components/PhaseStepper.tsx` | Zone 2 stepper, deterministic progression through phases Phi-1 to Phi-7 |
| 4 | `DrakonCanvas` | `src/components/DrakonStudio/DrakonCanvas.tsx` | Main visual logic canvas embedding `drakonwidget.js` |
| 5 | `DrakonToolbar` | `src/components/DrakonStudio/DrakonToolbar.tsx` | Zoom, pan, undo, redo, save, pseudocode modal trigger, view mode tabs |
| 6 | `DrakonIconPalette` | `src/components/DrakonStudio/DrakonIconPalette.tsx` | Drag-and-drop / click-to-insert palette of 24 canonical DRAKON icons |
| 7 | `VisualFlowCanvas` | `src/components/DrakonStudio/VisualFlowCanvas.tsx` | Simplified vertical skewer visualizer (pure SVG/React fallback) |
| 8 | `NodeInspector` | `src/components/DrakonStudio/NodeInspector.tsx` | Property editor for selected DRAKON node (labels, conditions, ADR mapping) |
| 9 | `PseudocodeModal` | `src/components/DrakonStudio/PseudocodeModal.tsx` | Generates executable pseudocode (Python/TS) and AST tree from DRAKON diagram |
| 10 | `TimelineSlider` | `src/components/BitemporalRadar/TimelineSlider.tsx` | Dual-axis scrubber for Valid Time (Tv) and Transaction Time (Tt) |
| 11 | `AdrListCard` | `src/components/BitemporalRadar/AdrListCard.tsx` | Interactive list of active and superseded ADRs filtered by bitemporal lens |
| 12 | `AdrReaderModal` | `src/components/AdrReaderModal.tsx` | Full-text markdown viewer for individual ADRs with invariant extraction |
| 13 | `AdrLibraryModal` | `src/components/AdrLibraryModal.tsx` | Grid search, category filter, and full registry explorer for all ADRs |
| 14 | `CopilotStream` | `src/components/CopilotPanel/CopilotStream.tsx` | Streaming terminal for sovereign LLM assistance, context attachments, prompt dispatch |
| 15 | `ContextBadges` | `src/components/CopilotPanel/ContextBadges.tsx` | Toggles for context injection (ADR, DRAKON IR, Active Rules) into prompt |
| 16 | `TokenGauge` | `src/components/CopilotPanel/TokenGauge.tsx` | Word/token budget visualization against ADR-002 invariant (<500 words) |
| 17 | `ReviewGateModal` | `src/components/ReviewGateModal.tsx` | HITL Phi-6 decision gate (Approve with Ed25519 signature, or Reject & COW Branch) |
| 18 | `PipelineCatalogModal` | `src/components/PipelineCatalogModal.tsx` | Library of standard planar algorithm templates and B-SDD pipelines |
| 19 | `ProjectSwitcherModal` | `src/components/ProjectSwitcherModal.tsx` | Workspace and GitHub repository switcher with live GitHub API integration |
| 20 | `InvariantDrawer` | `src/components/InvariantDrawer.tsx` | Sliding drawer listing all active architectural invariants across ADRs |
| 21 | `TasksDrawer` | `src/components/TasksPanel/TasksDrawer.tsx` | Task checklist for current spec, with live toggle synchronization |
| 22 | `TelemetryDrawer` | `src/components/TelemetryDrawer.tsx` | Production SLA metrics, compiler latency charts, memory and error telemetry (ADR-012) |
| 23 | `MobileNavigation` | `src/components/MobileNavigation.tsx` | Bottom tab bar and drawer launcher for mobile devices |
| 24 | `MobilePhaseView` | `src/components/MobilePhaseView.tsx` | Mobile-optimized view of phase stepper and active sprint progress |
| 25 | `MobileRadarView` | `src/components/MobileRadarView.tsx` | Mobile-optimized bitemporal radar and timeline view |

---

## 3. Detailed Audit of Interactive Controls & 'Dead Buttons'

### 3.1 Dead Action: MobileNavigation missing ADR Library Button
- **Location:** `b-sdd-ui/src/components/MobileNavigation.tsx:24, 28-36`
- **Symptom:** In `App.tsx:611`, `onOpenAdrLibrary={() => setIsAdrLibraryOpen(true)}` is passed into `MobileNavigation`. However, `MobileNavigation.tsx` omits this prop from its destructuring parameters, and no icon or button exists in the mobile bottom bar to open the ADR Library.
- **Operator Experience:** On mobile screens or in mobile preview mode, operators cannot access the full ADR library from navigation.
- **Remediation:** Destructure `onOpenAdrLibrary` in `MobileNavigationProps` and add an ADR Book icon button to the action bar section.

### 3.2 Dead Action: Pipeline Catalog Default Templates have empty nodes
- **Location:** `b-sdd-ui/src/components/PipelineCatalogModal.tsx:18-95`
- **Symptom:** All default templates in `DEFAULT_TEMPLATES` contain empty node arrays (`schema: { nodes: [] }`). In `App.tsx:149`, `handleLoadPipelineTemplate` guards loading with `if (tmpl.schema && tmpl.schema.nodes && tmpl.schema.nodes.length > 0)`. Because length is 0, clicking 'Apply in Studio' executes nothing and closes the modal without updating the canvas.
- **Operator Experience:** Operator browses standard algorithm catalog, selects 'Binary Search' or 'B-SDD Pre-Flight Pipeline', clicks 'Apply', and the canvas remains completely unchanged.
- **Remediation:** Embed valid canonical DRAKON-IR nodes from `src/drakon/templates/*.json` directly into `DEFAULT_TEMPLATES`.

### 3.3 State Drift: Visual Canvas Edits disconnected from React `drakonNodes`
- **Location:** `b-sdd-ui/src/App.tsx:531-533`
- **Symptom:** When a user alters node text or creates links directly inside the `drakonwidget.js` canvas, `DrakonCanvas` calls `onDiagramChange`. In `App.tsx`, this callback is bound to `console.log('[Workbench] Diagram edited:', newDiag.name)`. React state `drakonNodes` is NOT updated.
- **Operator Experience:** Any visual editing done on the DrakonWidget canvas is discarded upon saving or generating pseudocode, because `handleSaveSpec` and `PseudocodeModal` read from React state `drakonNodes`.
- **Remediation:** Implement `syncFromCanvas` which parses the updated Drakon diagram into canonical `DrakonNodeIR[]` and updates `setDrakonNodes`.

### 3.4 Stale Data: Pseudocode Modal ignores live node edits
- **Location:** `b-sdd-ui/src/components/DrakonStudio/PseudocodeModal.tsx:37-65`, `App.tsx:758`
- **Symptom:** `PseudocodeModal` accepts `diagramJson: currentDiagram`, where `currentDiagram` is bound to initial `liveDrakon.data.diagram || CANONICAL_DRAKON_DIAGRAM`. When an operator edits nodes via the `NodeInspector`, `drakonNodes` updates, but `currentDiagram` remains the static fallback.
- **Operator Experience:** Pseudocode generator output never reflects newly added actions or condition changes made in the Node Inspector.
- **Remediation:** Construct dynamic diagram JSON from current `drakonNodes` using `irToDrakonJson(drakonNodes)` before passing to `PseudocodeModal`.

### 3.5 Mock Trap: Copilot LLM Proxy returns canned string & ignores context
- **Location:** `src/server/workbench_server.py:1138-1175`
- **Symptom:** `handle_post_copilot_proxy` receives `prompt`, `slot`, and `attached_contexts` from `CopilotStream.tsx`. Instead of calling sovereign LLM Gateway (`http://192.168.3.184:18880/v1/chat/completions`), it streams four hardcoded text lines via SSE and discards all attached contexts (`[ADR]`, `[DRAKON]`, `[RULES]`).
- **Operator Experience:** Operator asks questions about specific architectural invariants or complex logic, but receives identical generic mock sentences every time.
- **Remediation:** Implement HTTP streaming client in `workbench_server.py` forwarding the enriched prompt with context injection directly to the sovereign LLM Gateway.

### 3.6 Broken Relative Path: Project Switcher 404 on Cloudflare Pages
- **Location:** `b-sdd-ui/src/App.tsx:157`, `src/components/ProjectSwitcherModal.tsx`
- **Symptom:** `handleSwitchProject` calls `fetch('/api/projects/switch', ...)` without prepending `API_BASE_URL`. On Cloudflare Pages, static hosting responds with 404 or index HTML fallback.
- **Operator Experience:** Switching workspaces or selecting a GitHub repository fails silently with a console warning.
- **Remediation:** Route project operations through `fetchWithFallback` or prepend `API_BASE_URL`.

### 3.7 Simulated Action: ReviewGate COW Branch does not execute Git
- **Location:** `src/server/workbench_server.py:1028-1051`
- **Symptom:** When the operator chooses 'Reject & Branch' at Phase Phi-6, the server returns `created_branch: cow-branch-<timestamp>`, but does not execute `git branch` or `git checkout -b` in the actual filesystem.
- **Operator Experience:** The UI indicates a rollback branch was cut, but checking `git status` or `git branch` reveals no new branch was created.
- **Remediation:** Execute `subprocess.run(['git', 'checkout', '-b', branch_name], cwd=ROOT_DIR)` when rejecting with COW branch.

### 3.8 Mock Security: Operator Signature is static string
- **Location:** `b-sdd-ui/src/components/ReviewGateModal.tsx:39-41`
- **Symptom:** The operator signature is hardcoded to a static string `ed25519:e4f3a...`. The user cannot input a key, generate a session keypair, or sign the sprint hash cryptographically.
- **Operator Experience:** The verification check is a facade rather than a true cryptographic human-in-the-loop gate.
- **Remediation:** Add WebCrypto API integration allowing the operator to generate or import an Ed25519 / ECDSA key and sign the sprint handoff digest.

### 3.9 Hardcoded Scrubbing: Timeline limited to 16 days in Sept 2026
- **Location:** `b-sdd-ui/src/components/BitemporalRadar/TimelineSlider.tsx:84-90`
- **Symptom:** `validTimeDay` and `txTimeDay` are fixed to range `1..16`, formatting dates as `2026-09-${day}`. Real commits and transactions outside this 16-day window cannot be scrubbed.
- **Operator Experience:** Bitemporal exploration is constrained to a hardcoded demo slice.
- **Remediation:** Query `GET /api/adrs/timeline_bounds` to determine actual minimum and maximum commit timestamps.

### 3.10 Invariant Mismatch: TokenGauge semantics
- **Location:** `b-sdd-ui/src/components/CopilotPanel/TokenGauge.tsx:35-51`
- **Symptom:** Title says 'Active Rules Token Budget', but compares raw words (`word_count / 500`). B-SDD compiler strictly enforces raw words (<500 words).
- **Remediation:** Update UI label to 'Active Rules Word Budget (<500 words)' and show token estimate as secondary information.

### 3.11 Production Mixed Content: Cloudflare Pages vs Local Server
- **Location:** `b-sdd-ui/src/lib/api.ts:31-33`
- **Symptom:** When loading `https://b-sdd-ui.pages.dev`, browser blocks requests to `http://localhost:8765` due to Mixed Content policy.
- **Remediation:** Support sovereign HTTPS tunnel endpoint (via Cloudflare Tunnel / Tailscale) or toggle a high-fidelity 'Interactive Standalone Simulator' mode with local browser state persistence.

---

## 4. Remediation Priority Matrix

| Priority | Defect / Issue | Effort | Impact on HITL Integrity |
|---|---|---|---|
| **P0** | Sync DrakonWidget canvas edits to React `drakonNodes` | Small | **Critical** (Prevents data loss during visual design) |
| **P0** | Populate Pipeline Catalog default templates with real nodes | Small | **Critical** (Eliminates dead 'Apply' button in catalog) |
| **P0** | Fix MobileNavigation missing ADR Library trigger | Trivial | **High** (Restores mobile parity for ADR exploration) |
| **P1** | Connect PseudocodeModal to live `drakonNodes` | Small | **High** (Ensures generated code matches visual schema) |
| **P1** | Forward Copilot stream to sovereign LLM Gateway (`.184:18880`) | Medium | **High** (Enables real AI pair programming with context) |
| **P1** | Execute real `git checkout -b` on Phi-6 Reject & Branch | Small | **High** (Enforces WORM immutability and branching) |
| **P2** | Dynamic bitemporal timeline bounds from Git / Utopia | Medium | **Medium** (Enables long-term temporal auditability) |
| **P2** | WebCrypto Ed25519 signing for HITL review gate | Medium | **Medium** (Authentic non-repudiation) |
| **P2** | HTTPS tunnel configuration for Cloudflare Pages live mode | Medium | **High** (Enables live workbench operation from mobile/remote) |
