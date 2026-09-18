# Handoff: B-SDD Operator Workbench — Astryx Zones B & D Redesign (v2)

## Overview

This bundle contains a **targeted redesign** of five components in the B-SDD Developer Workbench (repo: `maxfraieho/b-sdd`, package `b-sdd-ui/`) that fixes layout defects in **Zone B (DRAKON Studio toolbar/palette)** and **Zone D (Bitemporal Timeline)**, plus optimizes the Node Inspector and upgrades the ADR Library from a read-only viewer into a full **MADR 3.0 Reader + Editor + Amend** workflow.

**Core defects fixed:**

| # | Zone / Component | Defect | Fix |
|---|---|---|---|
| 1 | Zone D · `TimelineSlider.tsx` | `T_v` / `T_t` date chips + coloured pulse dots were absolutely-positioned and physically overlapped the ADR-001 card. | Rigid **2-column layout**: fixed `w-64` left column holds date slots + controls; right column is `flex-1 min-w-0 overflow-x-auto` and hosts the horizontally-scrolling ADR rail. Cards are `flex-shrink-0` so they can never slide under the left panel. |
| 2 | Zone B · `DrakonIconPalette.tsx` | 20+ DRAKON glyphs crammed into one horizontal strip caused visual noise. | **Segmented Astryx toolbox with 4 tabs**: `[Потік]`, `[Розгалуження]`, `[Цикли]`, `[Система]`. Amber accent for logic tabs, cyan for system tab. |
| 3 | Zone B toolbar · `DrakonToolbar.tsx` | No schema-mode switch. | New `LogicStructureSwitcher` — segmented control `[ Логіка (Flow) · amber | Структура (Structure) · cyan ]` with `inset-shadow` underline for the active tab. |
| 4 | `NodeInspectorModal.tsx` | Vertical drawer, low-contrast primary action, sprawling form. | Compact 2-column grid, explicit routing block (`1 — Down` / `2 — Down + Right`), separate ADR-invariant block with severity chips. Two clearly-contrasted footer actions: **[Застосувати зміни]** (emerald primary) and **[Видалити]** (rose destructive). |
| 5 | `AdrLibraryModal.tsx` | Static "Full Text Reader". | Dual-mode: **read** (Markdown viewer + invariants strip + Copy INV) and **edit** (MADR 3.0 form with Title / Status / Markdown body / editable invariants list). Buttons: `[+ Новий ADR]`, `[Редагувати]`, `[Amend (superseded_by)]`, `[Save Draft]`, `[Publish (accepted)]`. |

## About the Design Files

The `.html` file in this bundle is a **design reference prototype** — a self-contained React + Tailwind mockup that shows the intended look and behavior of the redesigned components. **Do not ship the HTML directly.** The target codebase is the existing Vite + React 19 + Tailwind CSS 4 app at `b-sdd-ui/`; the task is to **replace the five listed `.tsx` files** with the versions in this bundle (adapted paths shown below), matching the existing patterns for imports, primitives, and asset resolution.

If your codebase does not yet have a frontend, use React 19 + Vite + Tailwind — this is the stack the design was authored against.

## Fidelity

**High-fidelity (hifi).** All colors are exact hex values from the Astryx Swiss High-Tech Dark palette; all spacing and sizing are pinned to Tailwind utility classes; interactions (segmented switches, scrubbers, modal open/close, ADR read↔edit, node select→inspect) are fully wired in the prototype. The developer should recreate the layout pixel-for-pixel using the existing Astryx primitives already in the repo (`b-sdd-ui/src/components/astryx/primitives.tsx`: `Button`, `IconButton`, `Badge`, `Dialog`, `Segmented`, `Selector`, `Banner`, `AppShell`).

## Target repository layout

Files in this bundle map to the following paths in the target repository. The bundle uses a flat `components/` folder for convenience — remap when copying:

```
design_handoff_bsdd_workbench_astryx_v2/components/…          →   b-sdd-ui/src/components/…

components/BitemporalRadar/TimelineSlider.tsx                 →   b-sdd-ui/src/components/BitemporalRadar/TimelineSlider.tsx
components/BitemporalRadar/AdrListCard.tsx                    →   b-sdd-ui/src/components/BitemporalRadar/AdrListCard.tsx
components/DrakonStudio/DrakonIconPalette.tsx                 →   b-sdd-ui/src/components/DrakonStudio/DrakonIconPalette.tsx
components/DrakonStudio/LogicStructureSwitcher.tsx            →   b-sdd-ui/src/components/DrakonStudio/LogicStructureSwitcher.tsx   (NEW file)
components/DrakonStudio/NodeInspectorModal.tsx                →   b-sdd-ui/src/components/DrakonStudio/NodeInspectorModal.tsx      (replaces NodeInspector.tsx OR added alongside as modal variant)
components/AdrLibraryModal.tsx                                →   b-sdd-ui/src/components/AdrLibraryModal.tsx
```

`DrakonToolbar.tsx` in the current repo already imports `Segmented` from `astryx/primitives`. Add the new `LogicStructureSwitcher` next to (or in place of) the existing `viewMode` `Segmented` — see integration notes below.

---

## Design Tokens (Astryx Swiss High-Tech Dark)

**Colors (exact hex — pinned):**

| Token | Hex | Usage |
|---|---|---|
| `canvas` | `#090d13` | Root page background, canvas fill |
| `panel` | `#0d121c` | Panel surfaces (top bar, left rail, palette background, timeline left column) |
| `card` | `#141b27` | Card surfaces, buttons secondary, list item default |
| `card-hover` | `#1a2233` | Hover state for buttons/cards on `card` |
| `subtle` (border) | `#1e293b` | All subtle borders and dividers |
| `amber` (accent) | `#f59e0b` | Primary accent — DRAKON logic mode, ADR IDs, active socket, invariant highlights |
| `emerald` (accent) | `#10b981` | Success / Valid Time / active ADR / Apply Changes primary |
| `cyan` (accent) | `#06b6d4` | Transaction Time / Structure mode / info banners |
| `violet` (accent) | `#8b5cf6` | Amend action (superseded_by) |
| `rose` (destructive) | `#f43f5e` | Delete / worse-branch / fatal severity |

**Text colors:** `text-slate-100` (`#f1f5f9`) primary, `text-slate-200` body, `text-slate-300` labels, `text-slate-400` secondary labels, `text-slate-500` muted / metadata, `text-slate-600` inline separators.

**Typography:**

| Purpose | Family | Weight | Size (Tailwind → px) |
|---|---|---|---|
| UI body | `Inter` | 400/500/600 | `text-xs` 12 / `text-sm` 14 |
| Buttons, labels, chips | `JetBrains Mono` | 500/700 | `text-[10px]` 10 / `text-[11px]` 11 |
| Timestamps, ADR IDs, invariant IDs, code, node types | `JetBrains Mono` | 700 | `text-[11px]` 11 / `text-[13px]` 13 |
| Uppercase section headers | `JetBrains Mono` 700 uppercase | `text-[10px]` 10 with `tracking-widest` |

**Spacing (Tailwind):** `p-1 / p-1.5 / p-2 / p-2.5 / p-3 / p-4 / p-5` — no arbitrary paddings. Left column of Timeline is `p-3`, right rail is `p-3` with `gap-3`.

**Sizing constants:**
- Left rail (Zone C): `w-14`
- Top bar (Zone A): `h-11`
- DRAKON toolbar: `h-10`
- DRAKON palette tabs row: `h-8`, icon rail row: `h-10` (total palette height 72 px including borders)
- Bitemporal timeline strip: **`h-[168px]`** (fixed inline `style={{ height: 168 }}`)
- Timeline left column: **`w-64` (256 px) `flex-shrink-0`**
- ADR timeline card: **`w-56` (224 px) `shrink-0`**
- Buttons: `h-7` (small), `h-8` (medium), `h-10` (icon-only large)
- Node inspector modal: `max-w-2xl` (672 px), `max-h-[90vh]`
- ADR library modal: `max-w-6xl` (1152 px), body height `[72vh]`
- Copilot panel (Zone E): `w-72` (288 px)

**Border radius:** `rounded` (4 px) everywhere except cards (`rounded-lg` / 8 px), modal container (`rounded-lg`), pill states (`rounded-full` on Dot / dot markers only).

**Shadows:** `shadow-sm` on primary CTAs; `shadow-2xl` on modals; `shadow-[0_0_0_1px_rgba(16,185,129,0.15)]` on the selected ADR card in the timeline rail.

**Root invariant `FE-INV-01`:**
```css
html, body, #root { height: 100%; }
body { overflow: hidden; }   /* no page scroll — 100vh only */
```

---

## Screens / Views

The overall workbench is a single-page cockpit — one screen with five zones. This handoff focuses on Zones B (DRAKON Studio) and D (Bitemporal Timeline) plus two full-screen modals.

### Zone A — Top Bar (context only, not redesigned)

`h-11` panel background, left = hamburger + `B-SDD / Workbench` wordmark + branch chip; right = `[ADR Library]` opener + bell + user avatar.

### Zone C — Left Rail (context only, not redesigned)

`w-14` icon rail with 8 vertical navigation items (`Phase / DRAKON / Code / Tests / Telemetry / Copilot / Team / Terminal`). Active = amber tint (`bg-amber/15 text-amber border-amber/40`).

### Zone B — DRAKON Studio

Structure top-to-bottom:

1. **`DrakonToolbar` (`h-10`)**
   - Left cluster (`gap-3`):
     - Diagram name — `JetBrains Mono` 11 px, `truncate max-w-[220px]`.
     - `LogicStructureSwitcher` (NEW component, see below).
     - Planarity badge — outline `border-emerald/40 text-emerald bg-emerald/10`, `text-[10px]`, contains `CheckCircle` icon + `"Planar · 0 Crossings"`.
   - Right cluster (`gap-1.5`):
     - Undo / Redo — `w-7 h-7` icon buttons, `hover:bg-[#1a2233]`.
     - Separator `w-px h-4 bg-subtle mx-1`.
     - Zoom Out / Zoom In / Home.
     - Separator.
     - `[ADR Library]` outline button — `border-subtle bg-card hover:bg-[#1a2233]`.
     - `[Зберегти]` — primary emerald, `text-slate-950 font-bold`.

2. **`LogicStructureSwitcher` (NEW)**
   - Segmented pill: `bg-canvas border border-subtle rounded p-0.5`.
   - Two buttons, `h-7 px-3`.
   - **Logic** (default) — active: `bg-card text-amber font-bold` + `boxShadow: 'inset 0 -2px 0 #f59e0b'`.
   - **Structure** — active: `bg-card text-cyan font-bold` + `boxShadow: 'inset 0 -2px 0 #06b6d4'`.
   - Icons: `Workflow` (Logic), `LayoutGrid` (Structure) — 14 px, `text-current`.
   - Copy: `"Логіка"` + subtle `(Flow)` / `"Структура"` + `(Structure)`.

3. **`DrakonIconPalette` — segmented (72 px total)**
   - **Tabs row (`h-8`)**: header `"DRAKON Toolbox"` (amber `text-[10px]` uppercase `tracking-widest`) + 4-tab segmented control (`Потік / Розгалуження / Цикли / Система`). Active tab uses `boxShadow: 'inset 0 -2px 0 <accent>'` where accent = amber for `flow/branch/loop` tabs and cyan for `system`. Right-aligned counter: `"{n} фігур · [{activeTab}]"`.
   - **Icon rail (`h-10`)**: horizontal scroll of DRAKON glyph buttons for the currently-selected tab. Each button `h-7`, `px-2`, `gap-1.5`, contains a `w-4 h-4` glyph (bundled PNG in the repo — see Assets) + Cyrillic label in mono `text-[11px]`. Active socket type: `bg-amber text-slate-950 border-amber font-bold shadow-sm`.
   - **Tab → icon-id mapping** (must be preserved exactly — used by DRAKON widget schema):
     - `flow` → `b0` (header), `action`, `end`, `insertion`
     - `branch` → `question`, `select`, `case`
     - `loop` → `loop_start`, `loop_end`, `for_begin`, `for_end`
     - `system` → `timer`, `pause`, `duration`, `process`, `shelf`, `comment`, `address`

4. **DRAKON canvas** (delegates to existing `DrakonCanvas.tsx` / `VisualFlowCanvas.tsx` / JSON view — the prototype shows only a schematic mock; no changes required to the widget itself).

### Zone D — Bitemporal Timeline (`TimelineSlider.tsx` + `AdrListCard.tsx`)

Fixed strip at the bottom of the cockpit main area, `h-[168px]`, `border-t border-subtle`, `bg-canvas`. Rendered as a `flex` row.

**Left column — fixed `w-64 flex-shrink-0 border-r border-subtle bg-panel p-3 flex flex-col gap-2`.**

Contents top-to-bottom:

1. Header row:
   - `"Bitemporal Lens"` — amber `text-[10px]` mono uppercase `tracking-widest font-bold`.
   - Right side: pulse indicator (emerald `w-1.5 h-1.5 animate-pulse` + count) · dot separator · `{superseded} sup.`

2. **`T_v` slot** — `rounded-md border border-subtle bg-card px-2.5 py-1.5`:
   - Label row: emerald pulse (`animate-ping` ring + solid dot, both `w-2 h-2`) + `Calendar` icon + `"T_v"` label; right = date `"2026-09-DD"` mono bold `text-[11px]` `tabular-nums`.
   - `<input type="range">` styled with `accent-emerald` via `.tv` class. Height 4 px track, 14 px thumb, `bg-canvas` track.

3. **`T_t` slot** — identical structure, cyan variant (`.tt` class, `accent-cyan`).

4. **Controls row (`mt-auto`, `gap-1`)** — 4 buttons in the fixed 256 px width:
   - Step back — `flex-1 h-7`, icon `ChevronLeft`.
   - Play / Pause — `flex-1 h-7`, when playing: `bg-amber/15 border-amber/50 text-amber` + `"PAUSE"` label; when paused: default card + `"PLAY"` label. Auto-advances `validTimeDay` every 900 ms.
   - Step forward — `flex-1 h-7`, icon `ChevronRight`.
   - Reset — `w-7 h-7`, icon `RotateCcw`, resets both `T_v` and `T_t` to `maxDay` ("NOW").

**Right column — `flex-1 min-w-0 relative flex items-center`.**

- Subtle vertical grid background: `linear-gradient(to right, #1e293b 1px, transparent 1px)` at `80px` interval, `opacity-40`, `pointer-events-none`.
- Two edge-arrow scroll buttons — `absolute left-1 / right-1`, `w-6 h-6 rounded-full bg-panel/90 border border-subtle`, z-10. Each scrolls the rail by ±320 px.
- **Rail**: `ref={railRef}`, `flex-1 overflow-x-auto overflow-y-hidden p-3 flex gap-3 items-center min-w-0 scroll-smooth`. Contains `AdrTimelineCard` list.

**`AdrTimelineCard` (formerly `AdrListCard`) — `w-56 shrink-0`:**

- Container: `rounded-lg border px-3 py-2.5 transition-all`, three states:
  - **Active** (default): `bg-card border-subtle hover:border-emerald/50`.
  - **Active + selected**: `bg-emerald/10 border-emerald ring-1 ring-emerald/40 shadow-[0_0_0_1px_rgba(16,185,129,0.15)]`.
  - **Superseded**: `bg-panel/60 border-subtle opacity-55` (grayscale look via reduced opacity).
  - **Pending** (`startDay > validTimeDay`): `bg-panel border-dashed border-subtle opacity-70`.
- Row 1: `FileText` icon (amber when active, slate-500 otherwise) + ADR id (mono bold `text-[12px]`) + state chip (`Active` emerald / `Sup.` slate with `line-through` / `Pending` cyan).
- Row 2: Title `font-medium text-[11px] leading-snug line-clamp-2`.
- Row 3 (conditional): superseded-by pointer with `ArrowRight` icon + target ADR id in amber.
- Row 4: invariant count with `ShieldCheck` icon + date `tabular-nums`.

**State determination:**

```ts
const startDay = parseInt(adr.date.split('-')[2], 10);
const endDay   = adr.valid_to ? parseInt(adr.valid_to.split('T')[0].split('-')[2], 10) : null;
const notYet     = startDay > validTimeDay;
const superseded = endDay !== null && validTimeDay >= endDay;
const active     = !notYet && !superseded;
```

### `NodeInspectorModal` (replaces / augments `NodeInspector.tsx`)

Modal (`fixed inset-0 z-50 bg-black/70 backdrop-blur-sm`) with container `max-w-2xl bg-card border border-subtle rounded-lg shadow-2xl max-h-[90vh]`.

**Header (`bg-panel border-b border-subtle px-4 py-3`)**: `FileCode` amber icon + `"Редактор вузла DRAKON"` mono bold + node id chip (amber `bg-amber/10 border-amber/30`). Right: close X.

**Body sections (padding `p-4 space-y-3`):**

1. **Row 1 — 2-column grid (`grid grid-cols-3 gap-3`)**:
   - `col-span-2`: `Назва вузла` — `<input h-8>`, focus ring `border-amber ring-amber/30`.
   - `col-span-1`: `Тип` — `<select h-8>` with 5 options: `action / question / headline / address / end`.

2. **Detailed text** — `<textarea rows={3}>`, mirrors the label field.

3. **Маршрутизація block** (`rounded border border-subtle bg-panel p-3`):
   - Header with segmented `1 — Down` / `2 — Down + Right`. `question` type forces `two` (button `1` is disabled).
   - 2-column grid: **Down** (emerald label, `ArrowDown` icon) and **Right** (rose label, `CornerDownRight` icon). When routing is `one`, the Right column is `opacity-40 pointer-events-none`.
   - Footer note: `"Правило «Right is Worse»: права гілка веде до обробки помилки або відкату."` — slate-500 mono `text-[10px]`.

4. **ADR invariant binding block** (`rounded border border-subtle bg-panel p-3`):
   - Header: `Shield` amber icon + `"Прив'язка до інваріанту ADR"`.
   - 3-column grid: `adr_invariant_id` (col-span-2 select of all invariants across ADRs) + `Severity` (col-span-1, three chips `normal / severe / fatal`). Severity buttons are disabled until an invariant is selected. Tones:
     - `normal` — `bg-emerald/20 text-emerald border-emerald/50`
     - `severe` — `bg-amber/20 text-amber border-amber/50`
     - `fatal` — `bg-rose/20 text-rose border-rose/50`

**Footer (`bg-panel border-t border-subtle px-4 py-3 flex items-center justify-between`)**:
- Left: `[Видалити]` — `border-rose/50 bg-rose/10 text-rose hover:bg-rose/20`, `Trash2` icon.
- Right: `[Скасувати]` (card ghost) + `[Застосувати зміни]` (`bg-emerald text-slate-950 font-bold shadow-sm`, icon `Save` → `Check` on 1.5 s saved-flash).

### `AdrLibraryModal` — Reader + Editor

Modal `max-w-6xl`, header identical to Astryx `Dialog`.

**Left column — `w-80 shrink-0 border-r border-subtle bg-panel/60`:**

- Top block (`p-3 border-b border-subtle space-y-2`):
  - Search input — `h-8` with `Search` icon inside; live-filters by ADR id, title, and content.
  - **`[+ Новий ADR]` button** — full-width `h-8 rounded bg-amber text-slate-950 font-bold shadow-sm`. Opens editor with a fresh MADR draft.
- List — `overflow-y-auto p-2 space-y-1.5`. Each item: ADR id (amber mono bold) + status badge + title `line-clamp-2` + footer row `{n} INV · date`. Selected: `bg-[#1a2233] border-amber/60`.

**Right column — Reader mode (`bg-canvas`):**

- **Topbar** (`bg-panel border-b border-subtle px-5 py-3`): ADR id chip + title + `file_path` code + date. Right side: `[Редагувати]` (card ghost, `Pencil` icon) + `[Amend]` (`border-violet/40 bg-violet/10 text-violet font-bold`, `GitBranch` icon).
- **Invariants strip** (`bg-panel/80 border-b border-subtle px-5 py-2`): amber `"Інваріанти:"` label + inline chips per invariant with a Copy button (`Copy` → `Check` on flash, 1.5 s).
- **Markdown viewer**: `p-6 font-mono text-[13px] leading-relaxed bg-canvas text-slate-200 whitespace-pre-wrap`. If no content, centered slate-500 placeholder.

**Right column — Editor mode:**

- **Topbar**: draft id chip (cyan tone) + `"Editor · MADR 3.0"` + status label. Right: `[Read Mode]` (card ghost, `Eye` icon).
- **Body** (`p-5 space-y-4`):
  1. Title (col-span-2 input `h-8`) + Status select (`proposed / accepted / deprecated / superseded`) — 3-col grid.
  2. MADR body — `<textarea rows={14}>` mono `text-[12px]`, hint below listing the 4 sections in amber.
  3. Invariants editor — `rounded border border-subtle bg-panel p-3`, header with `[+ INV]` button, then rows of `[id input w-32] [statement input flex-1] [trash w-7]`.
- **Footer**: `[Скасувати]` + `[Save Draft]` (card, `Save` icon) + `[Publish (accepted)]` (emerald primary).

**Amend flow:** `startAmend()` clones the current ADR, generates a new incremental id `ADR-{n+1}`, pre-fills the Markdown body with a `> Supersedes **<current.id>**.` header, and drops the user into edit mode.

---

## Interactions & Behavior

- **Timeline play** (`900 ms` interval): `useEffect` timer advances `validTimeDay`; wraps `minDay` when reaching `maxDay`.
- **Timeline scrubber**: dragging updates `validTimeDay` / `txTimeDay`. Cards re-evaluate their `active` state on every tick.
- **Timeline rail arrow buttons**: `railRef.current.scrollBy({ left: ±320, behavior: 'smooth' })`.
- **DRAKON tab switch** (Palette): re-filters `DRAKON_ICONS` by `tab`; active tab uses inset shadow underline.
- **Logic / Structure switch**: swaps schema-view mode; passes value up to the parent for the canvas.
- **Node click** (canvas → inspector): opens `NodeInspectorModal`. `question` node type auto-forces `routing="two"` on load and when the user changes type to `question`.
- **Save flash**: `handleSave()` sets `isSaved=true` for 1.5 s, swapping the button icon `Save → Check` and the label `"Застосувати зміни" → "Збережено"`.
- **ADR Library search**: case-insensitive substring match across `id / title / content`.
- **Copy invariant id**: `navigator.clipboard.writeText(inv.id)`; button icon swap `Copy → Check` for 1.5 s.
- **Publish vs Save Draft**: Publish sets `status: 'accepted'`; Save Draft sets `status: 'proposed'`. If the draft id already exists in the list, `onSaveAdr` fires; otherwise `onCreateAdr`.
- **Amend**: creates a new ADR with `superseded_by = <original.id>` set in Markdown body — the wired backend contract is a `POST /api/adr` with `supersedes: <original.id>` field (existing repo pattern in `docs/decision/HANDOFF_BACKEND.md`).

## State Management

Component-local `useState` for all interactive state. In the parent `App.tsx`:

```ts
const [validTimeDay, setValidTimeDay] = useState(17);      // 1..17 (September 2026)
const [txTimeDay,    setTxTimeDay]    = useState(17);
const [adrs, setAdrs] = useState<BitemporalAdr[]>(MOCK_ADRS);
const [selectedAdrId, setSelectedAdrId] = useState<string>('ADR-008');
const [nodes, setNodes] = useState<DrakonNodeIR[]>(MOCK_NODES);
const [selectedNode, setSelectedNode] = useState<DrakonNodeIR | null>(null);
const [schemaMode, setSchemaMode] = useState<'logic' | 'structure'>('logic');
const [adrLibraryOpen, setAdrLibraryOpen] = useState(false);
const [activeSocketType, setActiveSocketType] = useState<string | null>(null);
```

Wire the timeline `T_v` / `T_t` to `useLiveData` / `usePhaseRealtime` hooks that already exist in `b-sdd-ui/src/hooks/`. Wire ADR CRUD to `lib/api.ts` (`POST /api/adr`, `PATCH /api/adr/:id`, `POST /api/adr/:id/amend`).

## Integration Notes

1. **`DrakonToolbar.tsx`** — remove or keep the existing `Segmented` for widget/flow/json `viewMode` and add the new `LogicStructureSwitcher` before it. The design intent is that Logic/Structure is the schema-content axis and widget/flow/json is the render axis; both may coexist in the toolbar.
2. **`NodeInspector.tsx` vs `NodeInspectorModal.tsx`** — the existing repo file is a right-side drawer (`absolute right-3 top-12 bottom-3 w-88`). The new file is a centered modal. Product decision: modal supersedes drawer (per spec §4). Delete the old `NodeInspector.tsx` after wiring the modal into `DrakonCanvas.tsx` (`onSelectNode → setSelectedNode` state moves up to `App.tsx`).
3. **Types** — the new files consume the existing types verbatim (`BitemporalAdr`, `DrakonNodeIR`, `DrakonNodeType` from `@/types/adr` and `@/types/drakon`). No type changes required.
4. **Astryx primitives** — the new files intentionally use raw Tailwind classes for buttons (not the `<Button>` primitive) in some places to hit the exact 7 px / 8 px height contract; when refactoring, wrapping them in `<Button size="sm">` from `astryx/primitives.tsx` is acceptable if the height matches (`h-7`).
5. **DRAKON glyph assets** — the palette imports the existing PNGs from `@/assets/drakon/*.png`. New icon ids `loop_start`, `loop_end`, `for_begin`, `for_end` currently reuse `group-duration.png`, `group-duration-r.png`, `foreach.png`. If the backend emits distinct sprites, drop them into `b-sdd-ui/src/assets/drakon/` and update the map.
6. **FE-INV-01** — verify `body { overflow: hidden }` is still set in `b-sdd-ui/src/index.css`. It is in the current repo; the redesign preserves it.

## Files

Inside this bundle:

- `B-SDD Workbench Redesign.html` — self-contained React + Tailwind CDN prototype rendering all five zones with mock data. Open it locally or in the design tool to see all interactions live.
- `components/BitemporalRadar/TimelineSlider.tsx` — Zone D 2-column layout (final).
- `components/BitemporalRadar/AdrListCard.tsx` — Fixed-width ADR card for the timeline rail (exports `AdrTimelineCard`).
- `components/DrakonStudio/DrakonIconPalette.tsx` — Segmented 4-tab palette.
- `components/DrakonStudio/LogicStructureSwitcher.tsx` — NEW file: schema-mode segmented switcher.
- `components/DrakonStudio/NodeInspectorModal.tsx` — Optimized modal node editor.
- `components/AdrLibraryModal.tsx` — Reader + Editor MADR 3.0 library.

## Assets

DRAKON glyph sprites are already in the target repo at `b-sdd-ui/src/assets/drakon/*.png` (see repo tree). This bundle does **not** re-copy the PNGs — the `.tsx` files reference them via `@/assets/drakon/*.png` and Vite resolves them from the target codebase.

Fonts: `Inter` and `JetBrains Mono` from Google Fonts. In production, either self-host or keep the CDN link in `index.html`.

Icons: `lucide-react` (already a dependency of the target repo, per `b-sdd-ui/package.json`).

---

## Acceptance criteria (per defect)

1. ✅ Dragging the `T_v` scrubber never causes any pulse dot or date chip to overlap `ADR-001` card — verified because ADR cards live inside `flex-1 min-w-0 overflow-x-auto` and can never enter the fixed `w-64` left column's rectangle.
2. ✅ All 17 DRAKON glyphs are still reachable — verified by tab switching (`4 tabs × {4/3/4/7}` = 18 slots; `for_begin` and `for_end` alias to `foreach.png`).
3. ✅ `[Логіка | Структура]` switcher present in toolbar with amber / cyan active states.
4. ✅ Node inspector: `Застосувати зміни` uses emerald `#10b981` foreground on `#020617` (`text-slate-950`) with `shadow-sm` — contrast ratio > 7:1. `Видалити` uses rose `#f43f5e` on `#f43f5e1a` background — contrast ratio > 4.5:1.
5. ✅ ADR Library supports New / Edit / Amend / Save Draft / Publish through the editor state machine (`mode: 'read' | 'edit'` + `draft: BitemporalAdr | null`).
