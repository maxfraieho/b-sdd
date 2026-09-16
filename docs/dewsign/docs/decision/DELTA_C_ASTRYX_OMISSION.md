# ΔC · Astryx Design System Directive Omission

**Artifact Type:** Negative Invariant Vector (per ADR-007 Sprint Chaining Protocol)
**Cycle:** Sprint N (Frontend Design Phase) → Sprint N+1 (Phase 2 Code Build)
**Detected By:** Frontend Design Agent (Genspark)
**Detected At:** 2026-09-16
**Severity:** `warn` (not `err`) — виконанню PHASE2 не блокує, але деградує стратегічну готовність до Sprint N+2
**Status:** `proposed` — вимагає підпису Head Architect на Φ6 наступного циклу

---

## 1. Формальне визначення порушення

```
ΔC = {
  Invariant_A007_INV_02 :
    ∀ frontend_directive ∈ Sprint_N.artifacts :
      frontend_directive MUST propagate to next_sprint.md
      AND next_sprint.md MUST be consumed by Sprint_{N+1}.backend_agent

  Observed_Violation :
    frontend_directive = "docs/decision/PROMPT_BACKEND_AGENT.md"
    next_sprint.md = ".context/next_sprint.md" (from b-sdd@master)
    consumed_by_backend = FALSE

  Root_Cause :
    frontend_directive was authored in Genspark project scope,
    NOT propagated to b-sdd repository .context/ before Φ7 distillation.
    Backend agent's context inherited only ADR-008 + task-006 backlog,
    without Astryx design-system recommendation.

  Downstream_Impact :
    PROMPT_GENSPARK_PHASE2_WORKBENCH_CODE.md specifies:
      - React 19 + Vite + TypeScript + Tailwind (accepted)
      - Custom StyleX-free approach (missed Astryx layer)
      - Lucide-react icons (compatible with Astryx, no conflict)
    Migration to Astryx deferred by minimum 1 sprint cycle.
}
```

---

## 2. Що НЕ дістало до бекенд-агента

| Артефакт | Локація (створено) | Локація (треба було) | Статус |
|---|---|---|---|
| Astryx directive (директива міграції) | `<genspark-project>/docs/decision/PROMPT_BACKEND_AGENT.md` §3 | `b-sdd/.context/next_sprint.md` (розділ "Cross-Component Directives") | ❌ Втрачено |
| Astryx component mapping table | `<genspark-project>/docs/decision/PROMPT_BACKEND_AGENT.md` §5.3.3 | `b-sdd/docs/PROMPT_GENSPARK_PHASE2_WORKBENCH_CODE.md` §2 (Structure) | ❌ Втрачено |
| ADR-FE-001 (frontend architecture) | `<genspark-project>/docs/decision/ADR-FE-001-cockpit-architecture.md` | `b-sdd/docs/adr/ADR-FE-001-*.md` | ❌ Втрачено |
| HANDOFF_BACKEND (API contract) | `<genspark-project>/docs/decision/HANDOFF_BACKEND.md` | `b-sdd/docs/HANDOFF_BACKEND.md` або `b-sdd/.context/api_contract.md` | ❌ Втрачено |

**Загальний висновок:** канал `Genspark Design project` ↔ `b-sdd repository` наразі відсутній як формальний B-SDD-механізм. Виявлено критичний розрив в архітектурному контракті ADR-007.

---

## 3. Що бекенд-агент реально отримав

Дистиляція його вхідного контексту (за фактом виконаного `PHASE2` промту):

- ✅ `ADR-008-drakon-visual-logic-and-developer-workbench.md` — архітектура 4-зонного workbench
- ✅ `specs/004-multi-session-handoff-and-drakon/tasks.md` — task-006 "Port React/Vite visualization workbench from ai-drakon-scaffolder"
- ✅ Референс на `stepan-mitkin/drakonwidget` як **обов'язковий канонічний рушій** (критично важлива архітектурна вимога — фронт-агент цього не знав!)
- ❌ Мій `PROMPT_BACKEND_AGENT.md` — не потрапив
- ❌ Astryx як цільова дизайн-система — не згадана в PHASE2

**Побічний позитив:** бекенд-агент зафіксував вимогу до **DrakonWidget від Мітькіна** (`libs/drakonwidget.js`), яка була пропущена в моєму оригінальному прототипі. Це **зворотний ΔC від бекенда до фронту**, і його треба враховувати.

---

## 4. Двонаправлений ΔC

Формалізуємо **обидва** порушення для симетричного handoff'у:

### ΔC (FE → BE) · пропущено фронт-агентом

```
Δ_FE→BE = {
  missed_directive: "Astryx design system (facebook/astryx) as target UI library",
  reason: "Frontend directive not committed to b-sdd/.context/",
  consequence: "PHASE2 uses raw Tailwind instead of Astryx components",
  mitigation: "Defer Astryx integration to Sprint N+2 as a dedicated migration cycle"
}
```

### ΔC (BE → FE) · пропущено бекенд-агентом (виявлено при читанні PHASE2)

```
Δ_BE→FE = {
  missed_directive: "stepan-mitkin/drakonwidget MUST be the DRAKON rendering engine (not custom SVG)",
  reason: "Backend agent's ADR-008 was authoritative but not visible to frontend agent",
  consequence: "Frontend prototype used custom SVG viewer (7211 bytes of drakon.jsx code)",
  mitigation: "PHASE2 implementation replaces custom SVG with DrakonWidget adapter"
}
```

**Обидва порушення — симетричні:** ні один агент не бачив артефактів іншого, обидва зробили розумні локальні припущення, обидва повинні бути виправлені у наступному циклі.

---

## 5. Виправлення протоколу (пропозиція для ADR-007-INV-04 NEW)

**Пропонований новий інваріант:**

```
ADR-007-INV-04 · Cross-Agent Directive Propagation

∀ agent A produces artifact X targeted at agent B :
  X MUST be committed to `b-sdd/.context/next_sprint.md` under section
  "Cross-Component Directives" BEFORE Φ7 distillation dispatches Sprint_{N+1}

∀ agent B receives control at Sprint_{N+1} start :
  B MUST read `.context/next_sprint.md` "Cross-Component Directives" section
  as PART OF PRE-FLIGHT COMPILATION (Φ3),
  NOT as optional reading.

Violation Consequence :
  Sprint_{N+1} MUST proceed with local defaults + emit Δ_A→B negative
  invariant into `docs/decision/DELTA_C_*.md` for retro-inclusion in Sprint_{N+2}.
```

Це закриває клас помилок «фронт-бекенд слонів у різних кімнатах».

---

## 6. Що робити зараз (План примирення)

### 6.1 У цьому циклі (Sprint N+1, Phase 2 Code Build)

- ✅ **Виконую PHASE2 точно як написано** — React 19 + Vite + TS + Tailwind + Lucide + `stepan-mitkin/drakonwidget`. Ніяких Astryx-компонентів.
- ✅ **Створюю цей файл (`DELTA_C_ASTRYX_OMISSION.md`)** як формальний артефакт handoff'у.
- ✅ **Зберігаю Astryx-совместимість архітектурно:** Tailwind-класи → у наступному циклі механічно замінюються на Astryx-компоненти (`bg-surface` → `<Card>`, `<button>` → `<Button variant="primary">` etc). Без rewrite.

### 6.2 Наступний цикл (Sprint N+2)

**Ціль спринта:** `Migrate b-sdd-ui to Astryx design system + integrate real Utopia/LLM backend APIs`

**Вхідні артефакти:**
- Цей `DELTA_C_ASTRYX_OMISSION.md` (як негативний вектор інваріантів)
- `PROMPT_BACKEND_AGENT.md` §3 (директива міграції)
- `PROMPT_FRONTEND_MIGRATION.md` (буде створений бекенд-агентом ПІСЛЯ інтеграції реальних API)
- Готовий `b-sdd-ui/` проєкт (артефакт цього циклу)

**Очікуваний вихід Sprint N+2:**
- `b-sdd-ui/` з `@astryxdesign/core` замість raw Tailwind
- Кастомна `defineTheme()` з Swiss High-Tech Dark токенами
- Заміна `<button className="...">` → `<Button variant="..." />` за таблицею мапінгу
- CLI `astryx init` виконано, `AGENTS.md` / `CLAUDE.md` містять компонентний індекс
- ADR-FE-002 задокументовано: «Migration from Tailwind-only to Astryx»

### 6.3 На рівні протоколу (стратегічне)

- **Head Architect має додати `.context/next_sprint.md`** секцію `## Cross-Component Directives` після Φ7 кожного циклу.
- **Або** створити `.context/inter_agent_bus.md` — окремий файл-канал.
- **Або** імплементувати новий інваріант `ADR-007-INV-04` (див. §5) — оптимально.

---

## 7. Метаurl — dogfooding момент

**Цей файл сам є доказом працездатності B-SDD методології:**
- Виявлення порушення інваріанта → створення MADR / ΔC-нотатки.
- Не blame, а формалізація.
- Формалізація → runtime-перевірка в наступному циклі.
- Runtime-перевірка → неможливість повторити помилку.

Це саме той петля навчання, яку описує ADR-006 (`session_distillation`). Ми не просто пишемо код — ми еволюціонуємо сам протокол розробки.

---

## 8. Signatures

- **Автор ΔC:** Frontend Design Agent (Genspark), Sprint N (design phase)
- **Виявлено при читанні:** `docs/PROMPT_GENSPARK_PHASE2_WORKBENCH_CODE.md`, sprint N+1
- **Пропонується до включення:** `.context/next_sprint.md` наступного циклу
- **Awaiting sign-off:** Head Architect @ Φ6 gate (Volodymyr Kovalenko)

---

## Пов'язані артефакти

- `docs/decision/PROMPT_BACKEND_AGENT.md` — оригінальний директивний промт з Astryx-рекомендацією
- `docs/decision/ADR-FE-001-cockpit-architecture.md` — архітектура фронту, що осиротіла без потрапляння в b-sdd
- `docs/decision/HANDOFF_BACKEND.md` — API-контракт, теж не потрапив у b-sdd
- `b-sdd/docs/adr/ADR-007-multi-session-sprint-chaining-and-handoff.md` — базовий інваріант, який потребує розширення (INV-04)
- `b-sdd/.context/next_sprint.md` — точка втрати сигналу

**Кінець ΔC-нотатки.**
