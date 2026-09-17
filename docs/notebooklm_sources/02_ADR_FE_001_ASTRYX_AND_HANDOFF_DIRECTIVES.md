# B-SDD FRONTEND COCKPIT ARCHITECTURE, ASTRYX DIRECTIVES & HANDOFF

This document establishes the frontend architectural specifications, cross-agent handoff contracts, and the formal Delta-C analysis of design-system omissions between sprint cycles.

---

# ADR-FE-001 · Архітектура фронтенд-кокпіта B-SDD Operator Workbench

- **Status:** accepted
- **Date (T_v · valid):** 2026-09-16
- **Date (T_t · committed):** 2026-09-16
- **Deciders:** Genspark Design Agent · Volodymyr Kovalenko (Head Architect)
- **Consulted:** сусідній проєкт `drakonwidget` (референс візуальної мови ДРАКОН)
- **Superseded by:** —
- **Related:** ADR-008 (DRAKON-as-Spec Workbench), ADR-007 (Sprint Chaining), ADR-002 (Pre-Flight Compiler), ADR-024 (mTLS Tunnel)

---

## Context and Problem Statement

B-SDD методологія вимагає інженерного кокпіта оператора з чотирма одночасно активними інформаційними поверхнями (DRAKON-редактор, LLM-копілот, бітемпоральний ADR-таймлайн, шлюз рішень Φ6) та жорстким детермінованим автоматом фаз Φ1–Φ7. Стандартні UX-патерни консюмерських SaaS (tabbed layout, wizard, scrollable dashboard) руйнують ключову властивість Human-in-the-Loop: **одномоментну повну спостережуваність стану циклу**. Оператор має бачити одночасно топологію алгоритму, потік генерації, історію правил і кнопку блокуючого підпису — без перемикання контексту.

Треба ухвалити набір архітектурних рішень фронтенду, які **закріплюють цю щільність** і роблять кокпіт готовим до подальшої еволюції в продакшн-стек.

---

## Decision Drivers

- **HITL-детермінізм:** UI повинен унеможливлювати "проковтування" пропущеного стану — жодного вертикального скролу сторінки, всі критичні контроли завжди на екрані.
- **Bloomberg-density:** цільова аудиторія — інженер-архітектор на 1080p/1440p моніторі, який готовий читати щільну інформацію.
- **Ізольованість збоїв:** одна помилка в одному агенті не має обвалювати весь оператор-workbench (бо це саме той момент, коли оператор потрібен найбільше).
- **Пряма мапа UI ↔ Ф-стани:** фронт повинен бути дзеркалом бекенд-автомата, а не окремою моделлю.
- **Готовність до Vite/TS:** мінімальна відстань між прототипом і продакшн-збіркою.
- **Суверенність:** ніяких CDN-залежностей на аналітику, шрифти-only з Google Fonts (замінюваних на self-hosted у продакшні).

---

## Considered Options

### Що розглядалося для загальної структури

1. **Tabbed dashboard** (DRAKON / Copilot / Timeline / Gate у різних табах) — консюмерський, знайомий.
2. **Wizard step-by-step Φ1→Φ7** (по одному екрану на фазу) — просто, але руйнує паралельну спостережуваність.
3. **Fixed 4-zone grid + persistent gate bar** — щільно, все видно, але вимагає жорсткої дизайн-системи.

### Що розглядалося для стану

A. **Redux Toolkit / Zustand глобальний стор** — стандарт для складних додатків.
B. **React Context + локальний useState** — простіше, дешевше.
C. **Локальний state + Tweaks-панель + пізніша заміна на реальний Appwrite Realtime** — тимчасове, найшвидше для прототипу.

### Що розглядалося для рендеру DRAKON

X. **Повноцінний drakonwidget** із сусіднього репо (1.4 MB, drag-and-drop редактор).
Y. **Кастомний SVG-viewer** з ручними координатами + клікабельні вузли.
Z. **d3-hierarchy + автолейаут** — гарно, але непередбачувано для планарного шампуру.

---

## Decision

Ухвалено **6 архітектурних рішень**, які разом формують кістяк фронтенду.

### FE-D1 · Fiхована 4-зонна сітка 100vh без скролу сторінки

Оператор-workbench = один екран. `App.jsx` використовує CSS Grid:

```css
grid-template-rows: var(--topbar-h) var(--stepper-h) 1fr var(--timeline-h) var(--gate-h);
```

Внутрішні панелі скролюються локально; сторінка — ніколи. Це закріплює **інваріант "все критичне видно"** (FE-INV-01).

### FE-D2 · Дизайн-система через CSS-змінні, а не Tailwind arbitrary values

`:root` містить ~30 токенів (`--bg-*`, `--amber`, `--emerald`, `--violet`, `--rose`, `--font-*`, `--pad-*`). Усі кольори, відступи, розміри читаються тільки звідти. Це:

- Дозволяє миттєвий Density switch через `body[data-density]="dense|comfort"` — токени переоприділяються, компоненти нічого не знають.
- Готує ґрунт для тем (Deep Void / Graphite) без переписування компонентів.
- Спрощує міграцію в Vite/Tailwind: токени станут `theme.extend.colors`.

### FE-D3 · Локальний state зараз, Appwrite Realtime потім

Обрано варіант **C** (react useState + Tweaks). НЕ впроваджуємо Redux/Zustand:

- Прототип має один активний екран → глобального стору не потрібно.
- `data.js` виступає **явним контрактом DTO** для бекенду (див. HANDOFF § 6).
- При міграції: `data.js` → `src/mock/index.ts` → tanstack-query hooks (`useAdrs`, `useDrakon`, `useFitness`). Компоненти отримують дані через props, не через контекст → перехід прозорий.
- Виняток: `useTweaks(defaults)` з стартера — використовується тільки для оператор-preferences (density, activePhase override для демо).

### FE-D4 · React ErrorBoundary на кожну зону

Головний App обгортає **кожну зону окремо** у `<Boundary name="...">`. Обґрунтування:

- Human Review Gate — це саме той компонент, який має РАЗОМ з іншими рухами продовжувати працювати, навіть якщо, наприклад, DRAKON Studio впала.
- Крах = локальна червона плашка "Error in Timeline: ..." замість чорного екрана.
- Виявлено на власному досвіді: під час розробки один невірний доступ до `.title` в ReviewGate знищив увесь workbench. Після додавання Boundary — падає тільки одна зона, решта інтерактивна.

### FE-D5 · DRAKON як власний SVG-viewer, не drakonwidget

Обрано **варіант Y** (кастомний SVG). Причини:

- `drakonwidget.js` = 1.4 MB (жирно для прототипу).
- Нам потрібен viewer, а не редактор — фаза Φ2 закриває топологію (ADR-008-INV-01).
- Клікабельний inspector — простіше на React, ніж інтегруватись у widget через events.
- Координати вузлів задаються вручну в `data.js` (як у літаку — планарність гарантована людиною, не автолейаутом).
- **Компенсація:** візуальна мова (пропорції ікон, кольори за типом, шампур зліва) відповідає стандарту ДРАКОН і сумісна з drakonwidget-експортом майбутнього.

### FE-D6 · Babel-standalone у прототипі, Vite у продакшні

`@babel/standalone` через `<script type="text/babel">` дозволяє **розробляти без будь-якого білд-кроку** прямо в Genspark Design. Це прискорює ітерації на порядок. Ціна:

- Console-warning "You are using the in-browser Babel transformer" — прийнятно на етапі дизайну.
- Кеш браузера буває агресивний → `?v=N` cache-bust параметри у `<script src>`.
- **При міграції у Vite:** всі `?v=N` видаляються, `.jsx` → `.tsx`, імпорти через ES-modules. Vite видасть хеш сам.

---

## Consequences

### Позитивні

- Оператор бачить **весь стан циклу за 1 секунду** без прокрутки чи перемикання.
- Крах одного компонента не блокує підпис сертифіката (найкритичніша дія).
- Дизайн-система — 1 файл `styles.css`, ~200 змінних, зрозумілих як фронтенд-, так і бекенд-агенту.
- `data.js` = виконуваний контракт: бекенд знає точну форму відповідей, фронт тестується без бекенду.
- Перехід у Vite/TS = механічна робота (перейменування + видалення cache-bust), ніякої архітектурної переробки.

### Негативні (усвідомлені trade-offs)

- **Ручні координати DRAKON** — при додаванні нового вузла треба вручну зсувати сусідні. Приймається, бо схеми маленькі (5–15 вузлів) і планарність важливіша за автоматизацію.
- **Немає TypeScript** на цьому етапі — рефакторинг великих компонентів ризикованіший. Компенсується Boundary-ізоляцією та коротким життєвим циклом прототипу.
- **Немає віртуалізації** для довгих списків (наприклад, 1000 ADR) — прийнятно для першого етапу (<50 ADR).
- **Кожна панель скроллиться незалежно** — оператор може "загубити" вміст, який пішов за край. Компенсується мінімальним контентом на панель.
- **Babel-standalone уповільнює перше завантаження** на ~500ms — тільки в прототипі.

### Нейтральні

- Розмір бандлу (без Vite): ~140 KB JSX + 35 KB CSS + React 18 UMD з CDN. У Vite очікується ~180 KB gzipped total.
- Дві шрифтові родини (Inter + JetBrains Mono) → ~4 запити при першому завантаженні. Кешується назавжди.

---

## Pros and Cons of the Options (короткий підсумок)

### Загальна структура

| Опція | Плюси | Мінуси |
|---|---|---|
| **Tabbed dashboard** | знайомо, простий роутинг | руйнує HITL-спостережуваність — ❌ |
| **Wizard Φ1→Φ7** | лінійно, зрозуміло | приховує паралельний стан — ❌ |
| ✅ **Fixed 4-zone grid** | все видно, жорстка модель | вимагає дисципліни щільності |

### State

| Опція | Плюси | Мінуси |
|---|---|---|
| A. Redux/Zustand | масштабується, DevTools | overkill для одного екрана |
| B. Context + useState | без залежностей | більше пропсів |
| ✅ C. Local + Tweaks + пізніше Appwrite | найшвидший прототип, `data.js`=DTO | тимчасовий, треба замінити |

### DRAKON

| Опція | Плюси | Мінуси |
|---|---|---|
| X. drakonwidget | повний редактор | 1.4 MB, зайве для viewer |
| ✅ Y. Custom SVG | легкий, повний контроль | ручні координати |
| Z. d3-hierarchy | автолейаут | ламає планарність шампуру |

---

## Invariants Introduced (пропозиція для реєстру)

- **FE-INV-01:** `bodyOverflow(y) = hidden`. Порушення блокує PR.
- **FE-INV-02:** усі кольори у `.jsx` — тільки через `var(--*)`. Хардкоди `#XXXXXX` заборонені.
- **FE-INV-03:** кожна коренева зона `App` обгорнута в `<Boundary>`.
- **FE-INV-04:** `data.js` не містить логіки, тільки константи + JSDoc-типи, які дзеркалять DTO бекенду.
- **FE-INV-05:** DRAKON-вузол типу `action` або `question` ПОВИНЕН мати непорожнє поле `adr`.

---

## Links

- HANDOFF-документ для бекенду: [`HANDOFF_BACKEND.md`](./HANDOFF_BACKEND.md)
- Референс DRAKON widget: https://github.com/maxfraieho/drakonwidget
- Утopia DB endpoint: `https://192.168.3.251:9922`
- LLM Gateway: `https://192.168.3.184:18880`
- GitNexus AST: `https://192.168.3.184:4747`

---

## Notes

Цей ADR сам є артефактом B-SDD Φ1 (Intent Framing) — тобто фронтенд-архітектура запроектована **за тією самою методологією**, яку кокпіт обслуговує. Це `dogfooding`: workbench проектується інструментом, який він втілює.

Наступний ADR (FE-002) буде присвячений **міграції в Vite + TypeScript** — очікується після завершення Φ2/Φ3 бекенду (Utopia API готовий, тоді фронт переїжджає).


---

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


---

# Key Excerpts from Backend Handoff Contract (HANDOFF_BACKEND.md)

# HANDOFF · B-SDD Operator Workbench → Backend Engineering Agent

**Проєкт:** B-SDD Operator Workbench (Human-in-the-Loop Engineering Cockpit)
**Автор:** Frontend Design Agent (Genspark)
**Версія:** 3.0 (updated after Sprint N+2 · Phase 3 Live API & SSE Integration)
**Дата:** 2026-09-16
**Стан фронтенду:** Phase 3 виконана. Всі 5 API-контрактів + SSE-стрімінг підключені до `http://localhost:8765` з offline fallback. Готово до git merge у `maxfraieho/b-sdd@master → b-sdd-ui/`.
**Цільовий стек для UI-шарів бекенда:** **Astryx design system** (`@astryxdesign/core` — див. §11).

---

## 0. TL;DR (60 секунд)

Phase 3 інтегровано. **Скопіюй мою папку `b-sdd-ui/` у свій `b-sdd/b-sdd-ui/` (merge, не заміна)** — там нові файли `src/lib/{api,sse,backend-types}.ts`, нові хуки `src/hooks/{useLiveData,useCopilotStream}.ts`, модифіковані компоненти CopilotStream/ReviewGateModal/DrakonToolbar/App. Точний перелік у §12.

**Читай перед першим рядком коду:**
- `docs/decision/DELTA_C_ASTRYX_OMISSION.md` — критичний ΔC-вектор (не втрачай Astryx-контекст вдруге)
- `docs/decision/PROMPT_BACKEND_AGENT.md` — оригінальний директивний промт
- `docs/decision/ADR-FE-001-cockpit-architecture.md` — 6 архітектурних рішень фронту
- `b-sdd-ui/PHASE3_INTEGRATION.md` — детальний опис що зроблено у цьому спринті
- `b-sdd-ui/src/lib/backend-types.ts` — **виконуваний контракт DTO**: якщо твоя реальна відповідь не збігається — правь свій сервер, не мої типи
- `b-sdd-ui/src/data/mock*.ts` — форма мокових даних = точна форма живих відповідей

---

## 0.1 🔴 ДЖЕРЕЛО АРТЕФАКТІВ · Frontend Agent Workspace

**Цей файл (`HANDOFF_BACKEND.md`) знаходиться у master гілці `b-sdd` — це єдина копія, яку тобі гарантовано видно.**

**Всі інші артефакти, згадані у §0 «Читай перед першим рядком коду» та §12 «Перелік файлів для перенесення», зберігаються у робочому просторі Frontend Design Agent на платформі Genspark:**

```
Genspark Project ID: ab09b8da-5615-40e5-9075-63247e4ef05c
Project name:        design (B-SDD Operator Workbench)
Owner:               Volodymyr Kovalenko (Head Architect)
Structure:
    docs/decision/
        ├── HANDOFF_BACKEND.md                     (v3.0 · копія цього файлу)
        ├── ADR-FE-001-cockpit-architecture.md     (6 архітектурних рішень фронту)
        ├── DELTA_C_ASTRYX_OMISSION.md             (ΔC вектор інваріантів)
        └── PROMPT_BACKEND_AGENT.md                (директивний промт)
    b-sdd-ui/                                      (Phase 3 branch)
        ├── src/lib/{api,sse,backend-types}.ts     ⭐ NEW
        ├── src/hooks/{useLiveData,useCopilotStream}.ts ⭐ NEW
        ├── src/App.tsx                            ⭐ MODIFIED
        ├── src/components/CopilotPanel/CopilotStream.tsx ⭐ MODIFIED
        ├── src/components/ReviewGateModal.tsx     ⭐ MODIFIED
        ├── src/components/DrakonStudio/DrakonToolbar.tsx ⭐ MODIFIED
        ├── PHASE3_INTEGRATION.md                  ⭐ NEW
        ├── .env.example                           ⭐ NEW
        └── public/_headers, public/_redirects     ⭐ NEW/UPDATED
```

**Як тобі (агенту-розробнику) забрати артефакти:**

**Метод 1 (переважний) — прямий доступ через Genspark-інтеграцію:**
Якщо у твоєму runtime є Genspark connector, використай project ID `ab09b8da-5615-40e5-9075-63247e4ef05c` для читання файлів напряму. Це та ж модель доступу, якою я читаю твій `maxfraieho/b-sdd@master` (crossproject read).

**Метод 2 — попроси Head Architect:**
Якщо Genspark-connector недоступний — попроси Head Architect (Volodymyr Kovalenko) виконати одне з:
```bash
# Варіант A — ручний download через Genspark UI:
#   Відкриває проект → правий клік на b-sdd-ui/ → Download as ZIP
#   Розпаковує у b-sdd/ → git add . && git commit -m "sprint N+2: merge frontend Phase 3"

# Варіант B — якщо є HMAC/signed URL:
#   Head Architect генерує signed URLs для кожного файлу з §12
#   Агент викачує через curl і робить git commit локально
```

**Метод 3 — self-contained fallback:**
Якщо жоден з методів вище не спрацює, цей `HANDOFF_BACKEND.md` містить **достатньо специфікації** щоб ти міг реалізувати Phase 3 з нуля:
- §4 описує форму запитів/відповідей для кожного endpoint
- §6 містить повний API-контракт
- §7 — інваріанти які треба зберегти
- §12 — список нових файлів + який код у них має бути (посилання на релевантні секції)

Але це фолбек-варіант. **Правильний шлях — забрати вже написаний код з Genspark, а не переписувати.**

### Правило комунікації FE ↔ BE (ADR-007-INV-04 proposal)

Оскільки міжагентна комунікація через окремі workspaces створює ризик втрати контексту (див. `DELTA_C_ASTRYX_OMISSION.md`), пропоную новий інваріант:

```
∀ artifact A produced by Frontend Agent targeted at Backend Agent :
  A.canonical_location = 'genspark://ab09b8da-.../docs/decision/HANDOFF_BACKEND.md'
  AND A.reference_in_master = 'b-sdd/docs/decision/HANDOFF_BACKEND.md'
      (contains link to canonical + full spec text)

∀ Backend Agent starting new sprint :
  MUST read b-sdd/docs/decision/HANDOFF_BACKEND.md FIRST
  MUST resolve genspark://... link (or use fallback §12 spec) BEFORE Φ3 pre-flight
```

Формалізуй у `docs/adr/ADR-009-cross-agent-directive-propagation.md` якщо погодишся.

---

## 1. Файлова карта фронту (що вже існує)

```
b-sdd-ui/
├── package.json               # React 19 + Vite 6 + Tailwind 3.4 + lucide-react + clsx + tailwind-merge
├── vite.config.ts             # Alias @/* → src/*
├── tsconfig.json              # strict (noUnusedLocals: false для швидшої ітерації)
├── tailwind.config.js         # Swiss Dark palette + Φ-state keyframes
├── index.html                 # Google Fonts (Inter + JetBrains Mono)
├── .env.example               # VITE_API_BASE_URL=http://localhost:8765
├── PHASE3_INTEGRATION.md      # ⭐ NEW · детальний опис Phase 3 змін
├── public/
│   ├── _headers               # ⭐ UPDATED · CSP додає localhost:8765
│   ├── _redirects             # SPA fallback /* → /index.html
│   ├── favicon.svg
│   └── libs/drakonwidget.js   # stepan-mitkin v1.5.7 (1.39 MB)
└── src/
    ├── main.tsx · App.tsx · index.css
    │
    ├── lib/                                    # ⭐ Phase 3 backbone
    │   ├── api.ts                     ⭐ NEW · fetchWithFallback + POST wrappers
    │   ├── sse.ts                     ⭐ NEW · POST-based SSE via ReadableStreamDefaultReader
    │   ├── backend-types.ts           ⭐ NEW · DTOs mirroring workbench_server.py
    │   ├── utils.ts                   · cn() = twMerge(clsx(...))
    │   └── drakon/{adapter,ir-bridge,themeAdapter}.ts
    │
    ├── hooks/                                  # ⭐ NEW директорія
    │   ├── useLiveData.ts             ⭐ NEW · reactive poller + fallback + deps[]
    │   └── useCopilotStream.ts        ⭐ NEW · React state wrapper for SSE
    │
    ├── types/{adr,drakon,drakonwidget.d,sprint,copilot}.ts
    ├── data/{mockAdrs,mockDrakonSchema,mockSprints}.ts
    └── components/
        ├── Topbar.tsx · PhaseStepper.tsx · InvariantDrawer.tsx
        ├── ReviewGateModal.tsx        ⭐ MODIFIED · submitSprintReview + handoff panel
        ├── DrakonStudio/
        │   ├── DrakonCanvas.tsx
        │   ├── DrakonToolbar.tsx      ⭐ MODIFIED · + Save Spec button (4-state)
        │   └── NodeInspector.tsx
        ├── CopilotPanel/
        │   ├── CopilotStream.tsx      ⭐ MODIFIED · real SSE via useCopilotStream + Kill Stream
        │   ├── TokenGauge.tsx
        │   └── ContextBadges.tsx
        └── BitemporalRadar/{TimelineSlider,AdrListCard}.tsx
```

Файли позначені ⭐ — те, що треба **додати або оновити** у твоєму `b-sdd/b-sdd-ui/`. Все решта — вже в master після твого попереднього commit cc5abc0.

---

## 2. Автомат станів Φ1..Φ7 (як фронт очікує від бекенду)

Фронт зберігає активну фазу як `HitlPhaseId = 'phi_1' | ... | 'phi_7'` (див. `src/types/sprint.ts`). Для кожної фази `src/data/mockSprints.ts → phaseSnapshot` містить `HitlPhase` з `status: 'pending' | 'running' | 'completed' | 'blocked' | 'rejected'`.

**Критично:** Φ6 = єдина фаза з блокуючим Human Gate. Після Phase 3:
- `Approve & Cryptographically Sign` → викликає `POST /api/sprint/review { action: 'approve' }` → показує панель «Handoff dispatched» з `cycle_id`, `launch_command`, кнопкою copy.
- `Reject & Branch` → викликає `POST /api/sprint/review { action: 'reject', negative_invariants[], rationale, rollback_depth }` → показує панель «COW branch created» з `next_sprint_id`, `created_branch`.

**Клавіатурні скорочення (обробляються у `App.tsx`):**
- `Cmd/Ctrl+Enter` — Approve (тільки на Φ6)
- `Shift+R` — Reject & Branch (тільки на Φ6)
- `Escape` — закриває всі overlays

---

## 3. Дизайн-система (обов'язково для нових UI-артефактів)

Токени в `b-sdd-ui/tailwind.config.js`. **Не винаходь нових кольорів.** Мапінг на Astryx (для §11):

| Frontend token | Value      | Astryx equivalent                        | Purpose                      |
|----------------|------------|------------------------------------------|------------------------------|
| `canvas`       | `#070B12`  | `--color-background-body`                | глобальний фон               |
| `panel`        | `#0D1424`  | `--color-background-surface`             | панелі                       |
| `card`         | `#162035`  | `--color-background-card`                | картки                       |
| `border-subtle`| `#24324D`  | `--color-border`                         | 1px межі                     |
| `amber`        | `#F59E0B`  | `--color-status-warning` (customized)    | primary CTA, compilation     |
| `emerald`      | `#10B981`  | `--color-status-success`                 | tests OK, ADR accepted       |
| `violet`       | `#8B5CF6`  | `--color-hue-purple-vivid`               | AI-агенти, DRAKON, Φ6 gate   |
| `rose`         | `#F43F5E`  | `--color-status-error`                   | reject, violation            |
| `blue`         | `#3B82F6`  | `--color-hue-blue-vivid`                 | happy-path skewer            |
| `cyan`         | `#22D3EE`  | `--color-hue-teal-vivid`                 | T_t, silhouette              |

Шрифти: **Inter** (UI) + **JetBrains Mono** (код, invariants, timestamps).

---

## 4. Ключові UI-контракти

### 4.1 DrakonStudio (`components/DrakonStudio/`)

Використовує реальний `stepan-mitkin/drakonwidget` v1.5.7. Дані у форматі `DrakonSchemaIR` з `src/types/drakon.ts`. Обов'язкові інваріанти графа перевіряються серверним `src/drakon/validator.py` — не переписуй логіку на фронті.

**Phase 3 доповнення:** кнопка **💾 Save Spec** в `DrakonToolbar.tsx` викликає `saveDrakonSchema()` з `App.handleSaveSpec()`. Live-diagram береться через `canvasRef.current.exportJson()` і надсилається як `DrakonSchemaSavePayload` (див. §6.3).

### 4.2 Sovereign LLM Copilot (`components/CopilotPanel/CopilotStream.tsx`)

**Phase 3 переписаний повністю на реальний SSE:**
- Хук `useCopilotStream()` управляє fetch + ReadableStreamDefaultReader
- Кнопка **Kill Stream** з'являється під час активного стріму → викликає `abort()` через AbortController
- При помилці бекенду — inline банер `Sovereign gateway offline`, наступний prompt додасть fallback-повідомлення
- Токени прогресивно записуються у поточний assistant-бабл (не через batching)

**Форма запиту (сервер отримує):**
```json
POST /api/copilot/proxy
{
  "prompt": "Generate leaf action for cond_phi3",
  "slot": "coding-proxy",
  "stream": true,
  "attached_contexts": ["adr", "drakon"]
}
```

**Форма SSE відповіді (сервер має надсилати):**
```
data: {"type":"token","delta":"import "}\n\n
data: {"type":"token","delta":"json\n"}\n\n
data: {"type":"meta","slot":"coding-proxy","latency_ms":420}\n\n
data: {"type":"done","total_tokens":42}\n\n
```

Або скороченої форми `data: [DONE]\n\n` — теж парсимо.

### 4.3 Bitemporal Timeline (`components/BitemporalRadar/`)

**Phase 3 доповнення:** `App.tsx` тепер тримає `liveAdrs = useLiveData(...)` з `deps: [validTimeDay, txTimeDay]` — при кожному русі повзунка автоматично викликається `GET /api/adrs?valid_time=2026-09-XX&transaction_time=2026-09-XX`. Debounce робити не треба — deps через useEffect природньо гуртуються браузером.

### 4.
