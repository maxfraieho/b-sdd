# Handoff: B-SDD Operator Workbench · Astryx Edition

## Overview

This handoff packages the **B-SDD Operator Workbench · Astryx Edition** — a high-density Swiss engineering cockpit for driving the B-SDD (Bitemporal Spec-Driven Development) framework. The workbench is a single-page operator interface that composes 4 tightly-integrated zones:

1. **Topbar** — brand, sovereign node health, spec selector, action triggers, sync button
2. **HITL Phase Stepper** — 7-phase execution pipeline (Φ1 Intent Framing → Φ7 Distillation & Handoff)
3. **DRAKON Studio** — canonical DRAKON-as-Spec visual editor (17-icon palette + canvas + inspector) with a 3-mode view (Widget / Visual Flow / Raw IR JSON)
4. **Sovereign LLM Copilot Panel** — 3 model slots, Context Token Budget gauge (<500 words hard budget), live SSE stream
5. **Bitemporal ADR Radar** — dual T_v / T_t slider (Valid Time × Transaction Time) plus horizontal ADR strip
6. **Φ6 Review Gate Bar** (conditional, only when `currentPhase === 'phi_6'`) — blocking action strip: **Approve & Dispatch** vs **Reject & Branch** (Copy-On-Write snapshot protocol)

Plus 4 modals (ReviewGate, ADR Reader, Pseudocode Exporter, ADR Library) and 3 drawers (Invariants, Tasks, Node Inspector).

## About the Design Files

The files bundled here (`B-SDD Workbench Astryx.html` + `styles/` + `components/` + `lib/`) are **design references implemented in plain HTML + React 18 + Babel-standalone + inline JSX**. They are prototypes showing the intended visual language, layout, states, and interactions — **not production code to ship**.

The task is to **recreate these designs inside the existing `b-sdd-ui/` codebase** at [`github.com/maxfraieho/b-sdd`](https://github.com/maxfraieho/b-sdd) on branch `main`. That project already exists as a **React 19 + TypeScript + Vite** app and this design is the **Astryx-migration target** for its next sprint (`task-009: Migrate b-sdd-ui to Astryx design system components`, per the ΔC-ASTRYX-OMISSION directive at `docs/decision/DELTA_C_ASTRYX_OMISSION.md`).

**The developer must:**

1. Install `@astryxdesign/core` + `@astryxdesign/theme-neutral` + `@astryxdesign/cli` into `b-sdd-ui/package.json`.
2. Wire the strict CSS cascade layer in `b-sdd-ui/src/index.css`:
   ```css
   @layer reset, astryx-base, utilities;
   @import '@astryxdesign/core/reset.css' layer(reset);
   @import '@astryxdesign/theme-neutral/theme.css' layer(astryx-base);
   @import '@astryxdesign/core/tailwind-bridge.css' layer(utilities);
   ```
3. Override tokens with the Swiss High-Tech Dark palette (§ Design Tokens below).
4. Replace hand-rolled `<button>` / `<div>` chrome with Astryx components: `AppShell`, `TopNav`, `SideNav`, `Button`, `IconButton`, `TextInput`, `Selector`, `Dialog`, `AlertDialog`, `Banner`, `Toast`, `Card`, `Badge`, `Tag`, `Segmented`, `Theme`.
5. Preserve the **canonical `stepan-mitkin/drakonwidget.js`** from `public/libs/drakonwidget.js` — do **not** substitute React-Flow, Mermaid, or a custom SVG viewer. The SVG mock in `lib/drakon-mock.js` is only for design preview; production must use the real widget with `access: 'write'`, root branch `b0`, `showInsertionSockets(type)`, `startEditContent(nodeId)`, `showContextMenu()`.
6. Keep all live REST + SSE bindings to `http://localhost:8765` — the shape is already correct in `b-sdd-ui/src/lib/api.ts` and matches the mock adapter in `lib/api.js`.
7. `npm run build` (`tsc -b && vite build`) must succeed with **0 errors and 0 warnings** and `pytest` must pass **36/36** architectural fitness gates.

## Fidelity

**High-fidelity.** Pixel-perfect mockups with final Swiss High-Tech Dark palette, JetBrains Mono + Inter typography, exact spacing (Josef Müller-Brockmann 4/8/12/16/24 grid), Astryx primitive shapes, and all interactive states (hover / active / focus / disabled / running / rejected). The developer should recreate the UI pixel-perfectly using Astryx components — not visually reinterpret.

## Screens / Views

The workbench is a **single cockpit view** (never navigates away). Layout is `flex: column` filling `100vh × 100vw` with `overflow: hidden` (no page-level scrolling; scrolling is confined to internal panels, the DRAKON canvas, and code blocks).

### Zone 1 — Topbar (48px)

**Purpose:** Operator identity, project/branch context, sovereign VPC health, spec selection, and global action triggers.

**Layout:** Single horizontal flex row, `height: 48px`, `background: var(--color-bg-panel)` (#0d121c), `border-bottom: 1px solid #1e293b`, `padding: 0 12px`, `gap: 16px`. `flex-shrink: 0`. Items left-to-right:

| Group | Component | Details |
|---|---|---|
| Brand | 28×28 amber tile "B" + wordmark | `B-SDD WORKBENCH` (700, 12.5px, letter-spacing 0.02em) · `ASTRYX EDITION` muted · `v2.4.0 · B-SDD Framework Core · main @bffae39` (9.5px mono, muted+emerald+amber) |
| Divider | 1px vertical hair (`#1e293b`) | full-height |
| Spec selector | Astryx `Selector` | 240 min-width, `SPEC` eyebrow label, options: `001 · Compiler Core` etc. |
| Divider | 1px vertical | |
| Sovereign VPC | 3× `NodeIndicator` + Sync button | Each: `<Dot pulse tone="emerald"/>` + 2-line stack: label 10.5px bold + `192.168.3.251:9922` mono 9.5px in tone color. `Utopia DB`/`emerald`/`1.2ms` · `LLM Gateway`/`cyan`/`3 slots` · `GitNexus AST`/`cyan`/`idx`. Sync button: Astryx `Button size="sm" icon={syncIcon}` label `Синхронізувати` |
| `flex-grow: 1` spacer | | |
| Actions | 3× Astryx `Button size="sm"` | `Завдання` + amber outline `8/8` badge · `Бібліотека ADR` · `Інваріанти` + amber outline count badge |
| Divider | 1px vertical | |
| Operator | 24×24 amber-bordered tile `VK` + wordmark | `Volodymyr K.` (11px, 600) · `Head Architect` mono muted |

**Interactions:**
- `Sync` button — calls `POST /api/sync/utopia`, shows spinner in icon slot while `syncing === true`, then toast `✓ Utopia DB synchronized · 8 rulings · 1247ms`.
- Action buttons — open drawers/modals (see Interactions section).

### Zone 2 — HITL Phase Stepper (44px)

**Purpose:** Show all 7 phases of the B-SDD execution pipeline, current position, and status. Click any phase to jump.

**Layout:** Flex row `height: 44px`, `background: var(--color-bg-card)` (#141b27), `border-bottom: 1px solid #1e293b`, `padding: 0 12px`.

**Left rail:** `VERIFIED CYCLES` eyebrow + tabular `412 / 5,000` (amber 16px 700 + muted mono suffix), `border-right: 1px solid #1e293b`, `padding-right: 16px`.

**Phase cells:** 7 buttons, `flex: 1 1 0`, `min-width: 128px`, `padding: 0 12px`, `border-right: 1px solid #1e293b` between (except last). Each cell:
- 22×22 status tile (left): `border: 1.5px solid var(--color-[tone])`, `background: var(--color-[tone]-glow)` when done/active, `border-radius: 2px`, contents `Icons.check` if done else `p.index` (1..7), mono 10px 700.
- 2-line stack: `Φ1: Intent Framing` (11.5px 600, amber when active) + `100% Operator` (mono 9.5px muted).
- Right: `Dot tone="amber" pulse` when running.
- Active phase: `border-top: 2px solid var(--color-amber)` + `border-bottom: 2px solid var(--color-amber)` + `background: var(--color-bg-panel)`.

**Phase status → tone map:**
| Status | Tone | Tile fill |
|---|---|---|
| `completed` | emerald | emerald-glow |
| `running` / active | amber | amber-glow |
| `rejected` | rose | rose-glow |
| `pending` | muted (fg-faint) | transparent |

The 7 phases (canonical):

| ID | Symbol | Name | HITL Level | Validation Gate |
|---|---|---|---|---|
| `phi_1` | Φ1 | Intent Framing | 100% Operator | Zero conflicts with active ADRs |
| `phi_2` | Φ2 | Algorithmic Spec | 50% Supervision | Topological planarity & semantic bindings |
| `phi_3` | Φ3 | Pre-Flight Compilation | 0% Automated | Latency <50ms · Words ≤500 · 0 stale ADRs |
| `phi_4` | Φ4 | Phased Code Execution | 0% Automated | Control-flow topology immutability locked |
| `phi_5` | Φ5 | Automated Fitness Gates | 0% Automated | 100% pass rate · 0 external imports in `src/` |
| `phi_6` | Φ6 | Human Review Gate | 100% Chief Arch. | Cryptographic operator approval or Reject & Branch |
| `phi_7` | Φ7 | Distillation & Handoff | 20% Supervision | `sprint_handoff.json` & `next_sprint.md` verified |

### Zone 3 — DRAKON Studio (fills body height, right border to Copilot)

**Purpose:** Canonical DRAKON-as-Spec editing surface. **The centerpiece of the workbench.**

**Layout (nested column):**
1. **Toolbar** — 36px row, `background: var(--color-bg-panel)`, `border-bottom: 1px solid #1e293b`, `padding: 0 10px`, `gap: 10px`, `flex-wrap: nowrap`, `overflow: hidden`. Contents left→right: `DRAKON STUDIO` eyebrow + `004` cyan-outline Badge · divider · 5 IconButtons (zoom in/out, home, undo, redo, all `size="sm"`) · divider · Astryx `Segmented` with 3 options `Widget · Visual Flow · Raw IR JSON` · `flex: auto` spacer · mono `PLANAR crossings: 0 · nodes: 12` (emerald) · divider · Button `Псевдокод & Правила` (icon: code brackets) · primary Button `Зберегти (Ctrl+S)` (icon: save; spinner when saving; ✓ + "Збережено" for 1600ms on success).

2. **17-Icon Palette** — 48px row, **shown only when `viewMode === 'widget'`**, `background: var(--color-bg-card)`, `padding: 0 12px`, `gap: 12px`, `overflow-x: auto`, `align-items: center`. Groups separated by 1px×32 vertical dividers:
   - **Core** (6): `Дія` (action) · `Умова` (question) · `Вибір` (select) · `Варіант` (case) · `Гілка` (branch) · `Кінець` (end)
   - **I/O** (3): `Ввід` (input) · `Вивід` (output) · `Полиця` (shelf)
   - **Control** (6): `Процес` (process) · `Таймер` (timer) · `Пауза` (pause) · `Тривалість` (duration) · `Цикл` (foreach) · `Паралель` (par)
   - **Meta** (2): `Вставка` (insertion) · `Коментар` (comment)

   Each palette button: 46×38 min, `padding: 2px 4px`, 14×14 SVG glyph on top, 8.5px label below. Default `background: var(--color-bg-elevated)`, `border: 1px solid #1e293b`. Active (socket triggered): `background: var(--color-cyan-glow)`, `border: 1px solid var(--color-cyan)`, glyph and label become cyan.

   When any icon is active, right side shows `<Dot pulse cyan/> SOCKET · <TYPE>` inside a cyan-bordered pill (2px 8px padding, cyan-glow bg).

3. **Canvas** — fills remaining height, `overflow: auto`, `background: var(--color-bg-canvas)`. **Production must use the real `DrakonWidget` from `public/libs/drakonwidget.js`** with:
   - `access: 'write'`
   - Root branch `b0: { type: 'branch', branchId: 0, content: 'HITL Pipeline', one: firstNodeId }`
   - Node shapes: `action` (rect emerald), `question` (hexagon amber), `select` (trapezoid cyan), `end` (rounded rose), `branch` (headline violet with silhouette header bar), `process` (double-bar rect), `insertion` (dashed rect), `comment` (note-corner path)
   - Semantic bindings: each node carries `secondary: '[ADR-XXX-INV-XX]'` shown top-right in mono 9px amber
   - Right/false edge from `question` nodes rendered as **dashed rose line with `ні · no` label**
   - Double-click on any icon → `startEditContent(nodeId)` inline text editor
   - Right-click → `showContextMenu(x, y)` floating menu
   - Click on palette icon → `showInsertionSockets(type)` highlights valid drop targets

**Visual Flow view** (`viewMode === 'flow'`): fallback list of nodes as horizontal cards with severity color left border.

**Raw IR JSON view** (`viewMode === 'json'`): pretty-printed `<pre>` of the diagram JSON with `select-text`.

### Zone 4a — Sovereign LLM Copilot Panel (420px, right column)

**Layout:** Fixed `width: 420px`, `flex-shrink: 0`, column, `background: var(--color-bg-panel)`, `overflow: hidden`. Vertical sections:

1. **Header** (40px) — `⚡ SOVEREIGN LLM COPILOT` amber eyebrow · `SSE` cyan outline Badge · `mTLS` emerald outline Badge · mono `.184:18880`
2. **Model Slots** (auto height) — 3 stacked `SlotCard`s:
   - `agent-proxy` · `meta-llama/Llama-3.2-11B-Vision` · Fast architectural routing · ~0.6s
   - `coding-proxy` · `Qwen/Qwen2.5-Coder-32B-Instruct` · High-precision TS/Py AST · ~1.4s (active by default)
   - `reasoning-proxy` · `DeepSeek-R1-Distill-Qwen-32B` · Deep graph validation · ~3.1s

   Each card: `padding: 8px`, `background: var(--color-bg-card)`, `border: 1px solid #1e293b`, `border-left: 3px solid transparent`. Active card: amber-glow bg, amber 3px left border, name in amber.

3. **Token Budget** section — eyebrow `TOKEN BUDGET` + mono metric `476w / 500w · 14.5ms`. `TokenGauge` (12px bar, stacked segments emerald→cyan→amber, `border: 1px solid #1e293b`). Below: legend chips `Invariants 250w · Handoff 70w · DRAKON 156w` and skill badges `b-sdd · architecture-designer · skill-creator · find-skills`.

   **Over-budget state** (current > max): bar becomes solid rose, banner appears below: `⚠ BUDGET EXCEEDED · ADR-002-INV-02 violation · rollback required`.

4. **Stream** section (fills remaining height) — 6px header row with `STREAM` eyebrow, pause/play IconButton, `● live` (emerald) or `○ paused` (muted) mono indicator. Below: `<pre>` streaming buffer with monospace 11px content, `background: var(--color-bg-canvas)`, blinking `▊` caret in amber while streaming.

5. **CTA footer** — full-width Astryx `Button variant="primary" size="lg"` labeled `Відкрити Human Review Gate (Φ6)`.

### Zone 4b — Bitemporal ADR Radar (112px, bottom strip)

**Purpose:** Dual-axis scrubber over the last 30 days of ADR history, showing which invariants are active at the chosen `T_v` (Valid Time — domain reality) vs `T_t` (Transaction Time — physical commit log).

**Layout:** Flex row `height: 112px`, `background: var(--color-bg-card)`, `border-top: 1px solid #1e293b`.

- **Left meta** (220px, `border-right`): 22×22 cyan `R` tile + `Bitemporal ADR Radar` bold + `Utopia DB · pgvector · Tantivy` mono muted. Row of 2 stats: `ACTIVE` (emerald count) · `SUPERSEDED` (muted count). Below: `Δ (T_t − T_v) = 0d` cyan mono.
- **Center tracks** (flex-1): 2 stacked `TimelineTrack`s:
  - `T_v · Valid Time (domain reality)` (emerald tone)
  - `T_t · Transaction Time (physical commit log)` (cyan tone)
  
  Each track: label row + 24px timeline bar (`background: var(--color-bg-canvas)`, `border: 1px solid #1e293b`). Day tick marks every 5 days. ADR markers as 8×8 filled squares at their date with tone color + glow. Draggable **amber playhead** (2px vertical bar with 10×10 head above), `cursor: ew-resize`. Below: month labels `Sep 1 · Sep 8 · Sep 16 · Sep 24 · Sep 30` (mono 8.5px faint).

- **Right ADR strip** (340px, `border-left`): `Active ADRs @ T_v Sep 16, 2026` eyebrow + wrapped grid of small ADR pill chips (padding `3px 6px`, mono 10px 600). Each chip: dot + `ADR-001` etc. Selected chip becomes amber-glow.

### Zone 5 (conditional) — Φ6 Review Gate Bar (72px)

Shown only when `currentPhase === 'phi_6'`. Full-width strip below the main body + radar.

**Layout:** Flex row `height: 72px`, `background: var(--color-bg-panel)`, `border-top: 1px solid #1e293b`, `padding: 0 16px`, `gap: 20px`.

Left group: 44×44 amber gradient `Φ6` tile + column: `Human Review Gate` (13px 700) + amber `BLOCKING` Badge · description "All 5 upstream phases green · Fitness barriers passed · Awaiting synchronous operator sign-off" · mono amber `> AWAITING_HUMAN_SIGNOFF · sprint-2026-09-16-004`.

Middle group (5 metrics): `UNIT TESTS 25/25` · `AST ISOLATION 100%` · `COVERAGE 94.2%` · `LATENCY 16.4ms` · `TOKENS 476w`. Each: `min-width: 96px`, `white-space: nowrap`, eyebrow label + 15px 700 mono tabnum value in emerald + 9px muted mono unit line.

Right group: destructive Button `Reject & Branch` + `⇧R` mono keybind + success Button `Затвердити (Approve)` + `⌘⏎` mono keybind.

## Modals

### ReviewGateModal (960 × 640)

Two-column decision layout, split on center 1px divider.

**Left (Approve):**
- Emerald ✓ icon 40×40 in emerald-glow tile + heading `Затвердити та підписати` (emerald 15px 700) + subtitle `Approve & Dispatch to Φ7 Distillation`.
- `FITNESS GATES` eyebrow, then 5 `FitnessRow`s (label + value with ✓ mark in emerald if passing; `border-left: 2px solid var(--color-emerald)` on each row).
- Handoff markdown preview in mono 10.5px inside a canvas-bg box.
- Full-width `Approve & Dispatch` primary success Button at bottom + `Затвердити (⌘⏎)`.

**Right (Reject):**
- Rose branch-fork icon 40×40 in rose-glow tile + heading `Відхилити та створити гілку` (rose 15px 700) + `Reject & Branch · COW Snapshot Protocol`.
- `COW SNAPSHOT PROTOCOL` eyebrow + numbered 5-step list.
- Amber Banner with mono `ADR-008-INV-03 · ADR-007-INV-01` note about immutable audit.
- destructive Button `Продовжити (⇧R)` → transitions to **reject configure** sub-view.

**Reject configure sub-view** (replaces columns):
- Back button `← Back` + heading `Reject & Branch · Configure COW Snapshot`.
- `Branch Name` input (mono, default `cow/sprint-2026-09-16-004-<random-hex>`).
- `Rollback Depth` Selector (1/2/3 sprints).
- `Rejection Rationale (ΔC ledger)` textarea (min 120px, min 10 chars validation, character count below).
- Row: `Cancel` ghost Button + `Confirm Reject & Branch` destructive Button (disabled while reason < 10 chars).

### AdrReaderModal (1080 × 720)

**Structure:** Split row: content pane (`flex: 1`) + right rail (300px, `border-left`).

**Content pane:**
- **Preview mode:** rendered Markdown with custom styling. Headings: H1 (20px 700, border-bottom hair), H2 (15px 700 amber uppercase letter-spacing 0.02em), H3 (13px 600). Inline code: mono cyan on elevated bg. Code blocks: canvas bg + `border-left: 3px solid var(--color-amber)`. **Invariant IDs** (regex `ADR-\d+-INV-\d+`) auto-wrapped in cyan-glow pill Badge (mono 10.5px, `border: 1px solid var(--color-cyan)`).
- **Editor mode:** full-height `<textarea>` mono 12px on canvas bg, no border, `spellcheck=false`, `resize: none`. Fires `setDirty(true)` on change.

**Right rail:**
- `INVARIANTS (N)` eyebrow + list of invariant cards. Each card: `background: var(--color-bg-card)`, `border-left: 3px solid var(--color-[severity-tone])`, mono ID + severity Badge on top row, statement text below.
- `BITEMPORAL METADATA` eyebrow + label-value rows for `valid_from`, `valid_to`, `tx_time`, `supersedes`, `superseded_by`.

**Footer:**
- Left: file path + line/word/char counter + `unsaved changes` amber Badge if dirty.
- Right: Preview/Editor `Segmented` + primary `Зберегти (⌘S)` Button (spinner icon while saving, disabled unless dirty).

**Interactions:**
- **`Ctrl+S` / `⌘S`** keyboard shortcut → `POST /api/adrs/save` with `{ file_path, content }` → success toast `✓ ADR saved · recompiled active_rules.md`.
- Escape closes modal.

### PseudocodeModal (880 × 640)

Two-tab modal using Astryx `Segmented` in headerRight.

- **Tab 1 · Algorithmic Pseudocode:** Pythonic pseudocode generated from the diagram (function definition, if/else for questions, action calls with invariant comments, return for ends). Mono 12px `<pre>` on canvas bg.
- **Tab 2 · AST Rules Tree:** ASCII tree drawing (`├──`, `└──`, `│   `) of the diagram nodes with type prefix and content. Mono 12px muted color.

**Footer:** description + Copy Button (writes to clipboard, toast) + primary Download Button (saves as `hitl.pseudo.py` or `hitl.ast.txt`).

### AdrLibraryModal (860 × 640)

- **Filter bar:** search input (icon + placeholder `Search by ID, title, decision…`) + Selector filtering by component.
- **Rows:** each row `padding: 10px 16px`, `border-bottom: 1px hair`, `hover: bg-hover`. Columns:
  - 76px mono amber ID (`ADR-008`)
  - Title + decision outcome (14px 600 + 11px secondary truncated)
  - Right stack: emerald status Badge + cyan-outline component Badge + mono muted `T_v YYYY-MM-DD · N inv`
- Click row → opens `AdrReaderModal` with that ADR.

## Drawers (all right side, 420–480px wide, slide-in from right)

### InvariantDrawer (480px)

- Header: title + count Badge `N / total`.
- 3 SummaryChips in a row: `critical` (rose top border), `mandatory` (amber), `recommended` (cyan). Each shows count in tone color 16px 700 mono.
- Search input.
- Severity filter chips row: `all · critical · mandatory · recommended` with active pill highlight.
- List: invariant cards. Each card: `background: var(--color-bg-card)`, `border-left: 3px solid var(--color-[sev-tone])`, mono ID + severity Badge top row, statement, footer row with cyan-outline `ADR-XXX` Badge + mono `T_v YYYY-MM-DD → ∞` and `supersedes ADR-YYY` if present. Click → open AdrReaderModal with owning ADR.

### TasksDrawer (480px)

- Header: title + progress Badge `8/8 · 100%` (emerald when 100).
- Spec Selector.
- Spec info card: title bold + path mono muted.
- Task list: each row is a `<label>` with checkbox (accent-color emerald) + task ID mono muted + `done` Badge if complete + title (strikethrough when completed, muted color).
- Toggle fires `POST /api/tasks/toggle` and updates state locally.

### NodeInspectorDrawer (420px)

Opens when a canvas node is clicked.

- Header: title + cyan-outline node ID Badge.
- Type banner: full-width tinted box with `Dot` + uppercase type name (color varies: action=emerald, question=amber, end=rose, select=cyan, branch=violet).
- `LABEL · Мітка` — 60px min-height textarea.
- `Severity` — 5 button pills: `normal · mild · degraded · severe · fatal` with active tone pill highlighting.
- `Semantic Binding · ADR Invariant` — Selector with all invariants across all ADRs. When bound, shows below a cyan-bordered card with linked ADR title + `Click to open reader →` hint.
- `Edges` — mono readout `down → X · right → Y`.
- Footer: primary `Apply changes` Button + ghost `Cancel` Button.

## Interactions & Behavior

### Global keyboard shortcuts
- `Esc` — close any modal or drawer, deselect node.
- `Ctrl+Enter` / `⌘⏎` (when `currentPhase === 'phi_6'`) — open Review Gate modal.
- `Shift+R` (when `currentPhase === 'phi_6'`) — open Review Gate modal (pre-selects Reject).
- `Ctrl+S` / `⌘S` (inside AdrReaderModal) — save current ADR.

### Toasts
Bottom-center stack, `toast-in` slide-up animation 200ms. Auto-dismiss 2600ms. Tones: success (emerald border), error (rose border), info (default). Structure: `Dot` + optional title (12px 600) + message (11px secondary).

### Sync Utopia button flow
1. Set `syncing = true`, swap icon to spinner.
2. Await `POST /api/sync/utopia`.
3. Set `syncing = false`, toast success.

### Node selection flow
1. Click any canvas node with `data-node-id` attribute.
2. `handleNodeSelect(id)` → `setSelectedNodeId(id)` + `setShowNodeInspector(true)`.
3. Canvas re-renders with amber dashed outline on selected node.

### Palette icon → socket highlight flow
1. Click any palette button.
2. Toggle `activeSocketType` (click same again to deselect).
3. Canvas re-renders with cyan highlight boxes around all nodes of matching type.
4. In production: also call `canvasRef.current.showInsertionSockets(type)`.

### Approve flow
`Approve & Dispatch` → `POST /api/sprint/review { decision: 'approve', sprint_id }` → set `currentPhase = 'phi_7'` → success toast → close modal.

### Reject & Branch (COW) flow
`Confirm Reject & Branch` → `POST /api/sprint/review { decision: 'reject', parent_sprint_id, branch_name, reason, rollback_depth }` → set `currentPhase = 'phi_1'` → error toast `COW snapshot → <branch_name>` → close modal.

### Copilot streaming
- When `streaming === true`: append 1 chunk from `STREAM_SAMPLE` array every 420ms to buffer; truncate buffer to last 1400 chars when > 2000; auto-scroll pre to bottom.
- Pause button toggles `streaming`.

### Bitemporal scrubbing
- Mouse-down on track: set playhead to click position, enter drag mode.
- Mouse-move (while dragging): update playhead continuously.
- Mouse-up: exit drag mode.
- Day range: 1–30 (Sept 2026); position = `((day - 1) / 29) * 100%`.
- Right ADR strip filters to `activeAdrs = adrs.filter(a => parseInt(a.valid_from.slice(8,10)) <= playheadTvDay)`.

## State Management

Top-level state (all in root `AppInner`):

```ts
// Sovereign node & sprint state
const [health, setHealth] = useState(BSDD.HEALTH);
const [sprintState] = useMemo(...);   // derived from t.currentPhase + t.tokenBudget

// Spec & selection
const [specs, setSpecs] = useState(BSDD.SPECS);
const [selectedSpecId, setSelectedSpecId] = useState('004-multi-session-handoff-and-drakon');
const [selectedNodeId, setSelectedNodeId] = useState('cond_phi6');
const [activeSocketType, setActiveSocketType] = useState<string | null>(null);
const [selectedAdr, setSelectedAdr] = useState<Adr | null>(null);
const [activeSlotId, setActiveSlotId] = useState('coding-proxy');

// UI transient
const [saveState, setSaveState] = useState<'idle'|'saving'|'saved'|'error'>('idle');
const [syncing, setSyncing] = useState(false);

// Modal/drawer toggles
const [showReviewGate, setShowReviewGate] = useState(false);
const [showAdrReader, setShowAdrReader] = useState(false);
const [showPseudocode, setShowPseudocode] = useState(false);
const [showAdrLibrary, setShowAdrLibrary] = useState(false);
const [showInvariantDrawer, setShowInvariantDrawer] = useState(false);
const [showTasksDrawer, setShowTasksDrawer] = useState(false);
const [showNodeInspector, setShowNodeInspector] = useState(false);
```

Backend contract (all endpoints already typed in `b-sdd-ui/src/lib/api.ts` and mirrored in `lib/api.js`):

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Sovereign VPC status (Utopia, LLM, GitNexus) |
| `/api/rules/active` | GET | Pre-flight compilation snapshot + word count + latency + recommended skills |
| `/api/adrs?valid_time&transaction_time` | GET | Bitemporal ADR list at given coordinates |
| `/api/adrs/save` | POST | Persist ADR markdown → recompile active_rules.md |
| `/api/sync/utopia` | POST | On-demand Utopia DB sync |
| `/api/drakon/schema?spec=` | GET | Fetch DRAKON diagram for a spec |
| `/api/drakon/schema` | POST | Save + planarity-validate DRAKON schema |
| `/api/sprint/state` | GET | Current 7-phase state |
| `/api/sprint/review` | POST | Approve or Reject & Branch |
| `/api/projects` | GET | Repo/branch/workspace info |
| `/api/specs` | GET | Specs list with tasks |
| `/api/tasks/toggle` | POST | Flip a task's completed state |
| `/api/copilot/proxy` | POST | Sync LLM call |
| `/api/copilot/stream` | GET (SSE) | Live token stream |

Use `fetchWithFallback` pattern: attempt live fetch with `AbortController` timeout (~800ms), fall back to typed mock on network error so the workbench works offline (ADR-006-INV-01).

## Design Tokens

Copy these values verbatim into `b-sdd-ui/src/index.css` after the Astryx cascade imports:

### Colors (Swiss High-Tech Dark)

```css
:root {
  /* Surfaces */
  --color-bg-canvas:     #090d13;   /* base */
  --color-bg-panel:      #0d121c;   /* topbar, drawers, footers */
  --color-bg-card:       #141b27;   /* cards, radar, review bar */
  --color-bg-elevated:   #1a2233;   /* buttons, palette cells */
  --color-bg-hover:      #1f2937;   /* hover state */

  /* Borders */
  --color-border-hair:   #1e293b;   /* 1px hairlines */
  --color-border-strong: #334155;   /* focus/hover borders */
  --color-border-glow:   rgba(245, 158, 11, 0.35);

  /* Foreground */
  --color-fg-primary:    #e2e8f0;
  --color-fg-secondary:  #94a3b8;
  --color-fg-muted:      #64748b;
  --color-fg-faint:      #475569;
  --color-fg-inverse:    #0b0f16;

  /* Semantic accents */
  --color-amber:         #f59e0b;   /* active phase, primary CTA */
  --color-amber-soft:    #78350f;
  --color-amber-glow:    rgba(245, 158, 11, 0.15);

  --color-emerald:       #10b981;   /* verified, online, approve */
  --color-emerald-soft:  #064e3b;
  --color-emerald-glow:  rgba(16, 185, 129, 0.15);

  --color-cyan:          #06b6d4;   /* bitemporal, AST, info */
  --color-cyan-soft:     #164e63;
  --color-cyan-glow:     rgba(6, 182, 212, 0.15);

  --color-rose:          #f43f5e;   /* violations, reject, offline */
  --color-rose-soft:     #7f1d1d;
  --color-rose-glow:     rgba(244, 63, 94, 0.15);

  --color-violet:        #a78bfa;   /* headline / silhouette */
  --color-violet-soft:   #4c1d95;
}
```

### Spacing (Josef Müller-Brockmann grid)

```css
--sp-1: 4px;   --sp-2: 8px;   --sp-3: 12px;   --sp-4: 16px;
--sp-5: 24px;  --sp-6: 32px;  --sp-7: 48px;
```

### Radii (sharp)

```css
--r-none: 0;   --r-sm: 2px;   --r-md: 3px;   --r-lg: 4px;
```

Never use `border-radius` > 4px (except intentionally: `end`-type DRAKON nodes get `border-radius: 24px` for rounded shape; hex `question` nodes are polygons).

### Typography

```css
--font-sans: 'Inter', 'SF Pro Text', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, 'SF Mono', Menlo, monospace;
```

**Scale:**
| Class | Size | Weight | Letter-spacing | Use |
|---|---|---|---|---|
| `.text-eyebrow` | 9.5px mono | 600 | 0.14em, uppercase | section labels |
| `.text-label` | 11px | 500 | 0.02em | inline labels |
| `.text-metric` (`.mono .tabnum`) | varies | 600 | tabular-nums | numeric values |
| Zone titles | 12.5–13px | 700 | 0.01–0.02em | Topbar brand, section H2 in modals |
| Body | 11.5–13px | 400–500 | normal | descriptions |
| Modal H1 | 20px | 700 | -0.01em | ADR title in reader |

All numeric readouts (latencies, token counts, IDs, timestamps, ADR IDs) **must** use `font-family: var(--font-mono)` + `font-variant-numeric: tabular-nums`.

### Zone heights

```css
--h-topbar:    48px;
--h-stepper:   44px;
--h-toolbar:   36px;
--h-palette:   48px;
--h-radar:    112px;
--h-gatebar:   72px;
--w-copilot:  420px;
```

### Density modes (`body[data-density=…]`)

- `ultra`: row 24px, pad 8px, base 12px
- `standard` (default): row 32px, pad 12px, base 13px
- `comfort`: row 40px, pad 16px, base 14px

### Theme presets (`body[data-theme=…]`)

- `swiss` (default): as above
- `gothic`: darker canvas `#05060a`, panel `#0a0b12`, card `#12131c`, warmer amber `#eab308`
- `contrast`: pure `#000` canvas, primary `#fff` fg, saturated accents (`#ffb020`, `#22e88a`, `#22d3ee`, `#ff5b73`)

## Assets

**Preserved verbatim from `b-sdd-ui/src/assets/drakon/`** (26 canonical PNG icons for the DRAKON palette in the production build — the design prototype uses inline SVG glyphs instead but the developer should wire the PNG assets where the real widget expects them):

`action.png`, `branch.png`, `case.png`, `comment.png`, `ctrl-end.png`, `ctrl-start.png`, `duration.png`, `end.png`, `foreach.png`, `group-duration-r.png`, `group-duration.png`, `input.png`, `insertion.png`, `link.png`, `output.png`, `par.png`, `parblock.png`, `pause.png`, `process.png`, `question.png`, `select.png`, `shelf.png`, `silhouette.png`, `sinput.png`, `soutput.png`, `timer.png`.

**Preserved verbatim from `b-sdd-ui/public/libs/`**:
- `drakonwidget.js` (1.39 MB) — canonical `stepan-mitkin/drakonwidget` runtime. **MUST NOT** be substituted.
- `drakongen.js` (50 KB) — canonical pseudocode + AST generator (`diagramToPseudocode`, `diagramToTree`).

**Icons in this prototype** are hand-drawn inline SVGs (see `Icons.*` in `components/primitives.jsx`). In production, replace with `lucide-react` (already listed as compatible in `docs/decision/DELTA_C_ASTRYX_OMISSION.md`) or Astryx's built-in icon set.

**Fonts** are loaded from Google Fonts CDN in the prototype:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
```
In production, self-host under `b-sdd-ui/public/fonts/` and reference via `@font-face` inside the `astryx-base` layer to preserve offline parity (ADR-006-INV-01).

## Files

Design references in this bundle (mirror the intended production structure):

| Path | Purpose |
|---|---|
| `B-SDD Workbench Astryx.html` | Main entry point — loads React 18 + Babel and all script fragments |
| `styles/workbench.css` | All Astryx tokens + primitives styling (cascade-layered) |
| `lib/mock-data.js` | Typed mock data (ADRs, phases, sprint, diagram, slots, health, rules, stream) |
| `lib/api.js` | `fetchWithFallback` wrapper around `http://localhost:8765` |
| `lib/drakon-mock.js` | SVG mock renderer (prototype only — replace with `drakonwidget.js`) |
| `components/primitives.jsx` | Astryx-shaped Button, Badge, Dot, Banner, Selector, Segmented, Dialog, Drawer, Toast, Icons |
| `components/Topbar.jsx` | Zone 1 |
| `components/PhaseStepper.jsx` | Zone 2 |
| `components/DrakonStudio.jsx` | Zone 3 (toolbar + palette + canvas + IR views) |
| `components/CopilotPanel.jsx` | Zone 4a (slots + token gauge + SSE stream) |
| `components/BitemporalRadar.jsx` | Zone 4b (dual sliders + ADR strip) |
| `components/ReviewGateBar.jsx` | Φ6 blocking bar |
| `components/modals/ReviewGateModal.jsx` | Approve / Reject & Branch |
| `components/modals/AdrReaderModal.jsx` | Dual preview/editor + Ctrl+S save |
| `components/modals/PseudocodeModal.jsx` | Pseudocode + AST tabs |
| `components/modals/AdrLibraryModal.jsx` | Searchable ADR library |
| `components/drawers/InvariantDrawer.jsx` | Filterable invariant list |
| `components/drawers/TasksDrawer.jsx` | Spec task checklist |
| `components/drawers/NodeInspectorDrawer.jsx` | Node label/severity/binding editor |
| `app.jsx` | Root wiring: state, keyboard shortcuts, Tweaks panel, mount |
| `tweaks_panel.jsx` | Design-time tweak controls (dev only — strip before prod build) |

## Target Repository & Sprint Contract

**Destination:** `github.com/maxfraieho/b-sdd` branch `main`, subfolder `b-sdd-ui/`.

**Next sprint task:** `task-009 · Migrate b-sdd-ui to Astryx design system components` (per `docs/decision/DELTA_C_ASTRYX_OMISSION.md`).

**Verification runner (already in repo):**
```bash
./run_next_sprint.sh <path-to-this-handoff-folder>
```

**Success criteria:**
1. `cd b-sdd-ui && npm run build` → 0 errors, 0 warnings
2. DRAKON canvas renders with `access: 'write'`, root `b0` branch, 17-icon palette triggers `showInsertionSockets(type)`, double-click opens `startEditContent`, right-click opens `showContextMenu`, pseudocode export uses `diagramToPseudocode`.
3. All 12 REST endpoints wire correctly through `src/lib/api.ts` `fetchWithFallback`.
4. `pytest` → 36/36 architectural fitness gates pass (0 external imports in `src/`, planar DRAKON schemes, latency <50ms, tokens ≤500w).
5. Swiss High-Tech Dark palette applied via cascade-layered CSS custom properties over `neutralTheme`.
6. Bilingual UI preserved: Ukrainian for actions (`Завдання`, `Синхронізувати`, `Дія`, `Зберегти`, `Затвердити`, `Відхилити та створити гілку`), English for identifiers (`ADR-007-INV-02`, `Utopia DB`, `sprint_id`, `COW Snapshot`).
