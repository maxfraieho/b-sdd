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

### 4.4 Human Review Gate (`components/ReviewGateModal.tsx`)

**Phase 3 переписаний:** Approve/Reject тепер асинхронні (`isSubmitting: true` → loading spinner). Після успіху показується панель:

- **Approve response:** зелена панель з `cycle_id`, `worm_locked` badge, чорна CLI-плашка з `launch_command`, кнопка **copy** (2s зелена підсвітка після copy).
- **Reject response:** рожева панель з `created_branch`, `next_sprint_id`.
- **Backend error:** жовтий inline банер (не блокує локальний optimistic state).

---

## 5. State management (як зараз, що замінити НАДАЛІ)

Після Phase 3 багато state вже live. Що залишилось перевести:

| Фронт state             | Стан після Phase 3          | Наступний крок                       |
|-------------------------|-----------------------------|---------------------------------------|
| `activePhase`           | React useState              | Appwrite Realtime `sprints.{id}.phases` (Sprint N+3) |
| `sprintState.phases`    | React useState (моки)       | Real WS subscription (Sprint N+3)     |
| `selectedNode`          | React useState              | залишається локально                  |
| `playheadTv/Tt`         | React useState (live query) | зберігати в user preferences (Sprint N+3) |
| `streaming`             | ✅ Real SSE через useCopilotStream |                                |
| `mockAdrs`              | ✅ Live через getAdrs()      |                                       |
| `phaseSnapshot`         | React useState (моки)       | GET /api/sprint/state (Sprint N+3)    |
| `fitnessReport`         | React useState (моки)       | included у /api/sprint/state          |
| `tokenBudget`           | ✅ Live через getActiveRules() |                                     |
| `healthChips`           | ✅ Live через getHealth() polling 5s | треба UI badge у Topbar (Sprint N+3) |
| `llmSlots`              | Static (моки)               | included у /api/health.llm_gateway    |

---

## 6. API Contract (5 endpoints реалізовані)

### 6.1 Backend endpoint base

```
http://localhost:8765
```

Переоприділяється через `VITE_API_BASE_URL` у `.env.local` (див. `.env.example`).

### 6.2 GET endpoints — усі мають offline fallback у фронті

```typescript
// src/lib/api.ts

GET /api/health              → HealthResponse
GET /api/rules/active        → ActiveRulesResponse { compiled_snapshot, word_count, max_budget: 500, recommended_skills[], latency_ms? }
GET /api/adrs?valid_time&transaction_time
                             → AdrsResponse { adrs: BitemporalAdr[], total, valid_time?, transaction_time? }
GET /api/drakon/schema       → DrakonSchemaResponse { schema_ir, diagram, validation { is_valid, ... } }
GET /api/sprint/state        → SprintStateResponse { sprint_id, current_phase, can_approve, can_reject, fitness_summary? }
```

### 6.3 POST endpoints — БЕЗ automatic fallback

```typescript
POST /api/drakon/schema
  body: DrakonSchemaSavePayload { schema_ir, diagram?, target_path? }
  → DrakonSchemaSaveResponse { saved, target_path, validation, bytes_written? }

POST /api/sprint/review
  body: SprintReviewPayload {
    action: 'approve' | 'reject',
    negative_invariants?: string[],
    rationale?: string,
    rollback_depth?: number,
    operator_signature?: string,   // TODO Sprint N+3 — Ed25519 з Appwrite Auth
  }
  → SprintReviewResponse {
    action, sprint_id,
    // approve-specific:
    next_sprint_id?, cycle_id?, worm_locked?, launch_command?, handoff_path?, signature?,
    // reject-specific:
    created_branch?
  }

POST /api/copilot/proxy      → text/event-stream (див. §4.2)
  body: CopilotProxyPayload { prompt, slot, stream: true, attached_contexts?[] }
```

### 6.4 CORS

Фронт-dev працює на `http://localhost:5173`. Твій сервер має повертати:

```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Accept
```

Без цього браузер заблокує усі виклики.

---

## 7. Критичні інваріанти (НЕ ЛАМАТИ!)

- **ADR-002-INV-02:** `wordCount(activeRules) ≤ 500 AND compileTime < 20ms`. `TokenGauge` тепер бере `word_count` напряму з твого `GET /api/rules/active`.
- **ADR-024-INV-02:** SSE тільки через mTLS у sovereign VPC. CSP-headers у `_headers` дозволяють тільки `https://` для `.184/.251`; `localhost:8765` — dev-only виняток.
- **ADR-007-INV-01:** `handoff.next_sprint.md` містить `deltaC ∪ nextGoal AND signed(operator)`. Фронт показує `launch_command` у Approve-панелі ТІЛЬКИ якщо ти повертаєш `cycle_id` — без нього панель ховається (тобто фронт довіряє тобі валідацію).
- **ADR-008-INV-01:** DRAKON граф `planar = true AND crossings = 0`. Валідується у твоєму `src/drakon/validator.py`. При `POST /api/drakon/schema` повертай `validation.is_valid = false` + `violations[]` — фронт покаже стан `saveState = 'error'`.
- **ADR-008-INV-03:** AI generation scope = **тільки тіла leaf action-вузлів**. DrakonCanvas у read-only режимі (`canSelect: true`, але `startEditContent` no-op) — фронт не мутує топологію.
- **ADR-008 (Offline Parity):** ✅ Гарантується `fetchWithFallback` — усі GET мають fallback snapshot.
- **ADR-007-INV-04 (proposed):** Cross-Agent Directive Propagation — цей HANDOFF МАЄ потрапити у твій `.context/next_sprint.md → ## Cross-Component Directives` (див. §14).

Порушення інваріанту у твоїй відповіді → HTTP 422 з `{ inv: 'ADR-...', formula: '...', observed: '...' }`.

---

## 8. Тестовий сценарій End-to-End

```bash
# Terminal 1 — start backend
cd /path/to/b-sdd
python3 -m src.cli.main serve --port 8765

# Terminal 2 — start frontend
cd b-sdd-ui
npm install && npm run dev  # http://localhost:5173

# Або в один клік:
./run_workbench.sh
```

**9-кроковий сценарій приймання:**

1. Відкрити http://localhost:5173 — Topbar завантажує health chip.
2. **Copilot:** введи `Generate leaf action for cond_phi3` → бачити SSE стрім у реальному часі.
3. Клацни **Kill Stream** → потік чисто обірветься.
4. Введи новий prompt — має початися нова сесія (буфер очищений).
5. **Timeline:** перетягни T_v на 2026-09-10 → фронт зробить `GET /api/adrs?valid_time=2026-09-10&transaction_time=2026-09-16`.
6. **DRAKON Studio:** клацни **💾 Save Spec** → кнопка на 2.2s спалахне зеленим (успіх) або жовтим (validation.is_valid=false).
7. **Review Gate Approve:** Φ6 → Approve → з'явиться Handoff-панель з `cycle_id`, `launch_command`. Клацни **copy** → команда у clipboard.
8. **Review Gate Reject:** Φ6 → Reject & Branch → введи ΔC → Confirm → з'явиться панель `created_branch`.
9. **Offline test:** зупини бекенд → повтори кроки 2, 5, 6 → всі мають працювати з fallback повідомленнями без крашу UI.

**Якщо крок не працює після заміни моків — це bug у твоєму бекенді, не в моєму фронті.**

---

## 9. Що ЗАРАЗ НЕ реалізовано у фронті (треба буде додати)

- ❌ **Live health chip у Topbar** — `useLiveData` вже поллить `/api/health`, треба лише UI badge (Sprint N+3).
- ❌ **Ed25519 crypto sign** — поле `operator_signature` у payload існує, але не заповнюється. Треба Appwrite Auth JWT (Sprint N+3).
- ❌ **Двонаправлене редагування DRAKON вузлів** — Save Spec експортує тільки canonical IR; повне editing вимагає `canSelect: 'edit'` mode + розширення `ir-bridge.ts` (Sprint N+3).
- ❌ **Astryx-міграція** — відкладено на Sprint N+2/N+3 (див. `DELTA_C_ASTRYX_OMISSION.md` + §11).
- ❌ **Ліва бічна навігація, Billing, Sprint Handoff Console (Φ7)** — заплановано з Head Architect окремо.

---

## 10. Що ти маєш повернути мені — формат зворотного промту

Файл `docs/decision/PROMPT_FRONTEND_MIGRATION.md` (або `PROMPT_PHASE4.md` — назвіть як зручно, головне у папці `docs/decision/`).

Обов'язкові розділи:

### § 1. Що ти реально збудував / оновив
- Список ендпоінтів з реальними curl-прикладами (особливо запис SSE-потоку).
- **Розбіжності з моїм DTO (`b-sdd-ui/src/lib/backend-types.ts`).** Якщо ти був змушений змінити форму — обґрунтуй і я оновлю типи.

### § 2. CORS & auth статус
- `Access-Control-Allow-Origin` заголовки.
- Чи впроваджено Ed25519-підпис оператора (Sprint N+3 задача).

### § 3. Astryx Adherence Confirmation (обов'язково)
```markdown
- [ ] Я прочитав §11 HANDOFF та DELTA_C_ASTRYX_OMISSION.md
- [ ] Мої UI-артефакти (адмінка / email-шаблони / dashboards): [список або "немає"]
- [ ] Мої API-контракти сумісні з очікуваннями Astryx-компонентів
```

### § 4. Каталог питань до мене
Якщо щось незрозуміло — записуй як `[Q1] ..., [Q2] ...`.

### § 5. ΔC-вектор порушень мого прототипу
Якщо ти виявив порушення інваріанта у моєму коді — запиши як `ΔC = { ... }` для мого наступного циклу.

### § 6. Handoff CLI-команда
```bash
./run_b_sdd.sh --new-session "Sprint N+3: <твоя задача>"
```

---

## 11. 🔴 ОБОВ'ЯЗКОВЕ: Astryx Design System

Незмінно з v2.0. Стратегічне рішення Head Architect: **усі UI-артефакти системи** (фронт + бекенд-панелі/адмінки/email-шаблони) переходять на **Astryx** (`facebook/astryx`).

- Репозиторій: https://github.com/facebook/astryx
- Storybook: https://facebook.github.io/astryx/
- Пакети: `@astryxdesign/core`, `@astryxdesign/theme-neutral`, `@astryxdesign/cli`
- Requires React 19+ (наш стек готовий).
- CLI `npx @astryxdesign/cli init` пише компонентний індекс у `AGENTS.md` / `CLAUDE.md` для агентних роботів.

**Якщо ти будуєш будь-який UI-артефакт** — це:
- ✅ Адмін-панель Utopia DB
- ✅ DevOps-дашборд стану LLM Gateway
- ✅ Web UI Appwrite Console customization
- ✅ HTML email-шаблони sprint-summary
- ✅ Landing API-docs

**→ ЦЕ РОБИТЬСЯ ЧЕРЕЗ ASTRYX.** Ніякого власного Bootstrap/MUI/shadcn.

Мапінг наших компонентів на Astryx (для Sprint N+3):

| Наш компонент             | Astryx replacement                | CLI команда                              |
|---------------------------|-----------------------------------|------------------------------------------|
| `Topbar.tsx` health-cluster | `Toolbar` + `Badge` + `StatusMessage` | `astryx component Toolbar`             |
| `PhaseStepper.tsx`        | `Stepper`                          | `astryx component Stepper`               |
| `CopilotStream.tsx` slots | `Card` + `RadioGroup`              | `astryx component Card`                  |
| `TokenGauge.tsx`          | `Progress` (multi-segment)         | `astryx component Progress`              |
| `ReviewGateModal.tsx`     | `Dialog` + `ButtonGroup` + `Alert` | `astryx component Dialog`                |
| `NodeInspector.tsx`       | `Sheet` (Right)                    | `astryx component Sheet`                 |
| `DrakonCanvas.tsx`        | *(власний — Astryx не має графового)* | —                                     |

Форми API які я очікую сумісними з Astryx:
- Пагінація: `{ items[], total, cursor? }` — вже у `AdrsResponse`.
- Помилки: `{ code, message, details? }` — треба додати до всіх твоїх error responses.
- Realtime events: рекомендую `{ type, payload }` shape.

---

## 12. 🔴 Phase 3 — точний перелік файлів для перенесення у master

**Джерело:** Genspark project `ab09b8da-5615-40e5-9075-63247e4ef05c`, папка `b-sdd-ui/` (див. §0.1 для методів доступу).

**Дія:** merge (не заміна!) у `b-sdd/b-sdd-ui/` → `git commit`. Всі мої зміни зроблені на базі твого commit `cc5abc0` — конфліктів merge не має бути.

### Нові файли (git add)

| Path | Розмір | Призначення |
|---|---|---|
| `src/lib/backend-types.ts` | 4.3 KB | DTO мапінг твого workbench_server.py |
| `src/lib/api.ts` | 6.8 KB | fetchWithFallback + типізовані GET/POST wrappers + liveMode subscription |
| `src/lib/sse.ts` | 4.7 KB | POST-based SSE через ReadableStreamDefaultReader з AbortController |
| `src/hooks/useLiveData.ts` | 2.1 KB | Реюзабельний poller з reactive deps |
| `src/hooks/useCopilotStream.ts` | 2.4 KB | React state обгортка навколо sse.ts |
| `.env.example` | 0.4 KB | VITE_API_BASE_URL=http://localhost:8765 |
| `PHASE3_INTEGRATION.md` | 8.2 KB | Docs що зроблено (у самому `b-sdd-ui/`, не в `docs/`) |
| `public/_headers` | 0.8 KB | Cloudflare CSP з localhost:8765 у connect-src |
| `public/_redirects` | 0.1 KB | SPA fallback |

### Модифіковані файли (git diff → merge)

| Path | Що змінилося |
|---|---|
| `src/App.tsx` | Додано `useLiveData` хуки (health/rules/adrs), `handleSaveSpec` handler, live `TokenBudget` з реальної Pre-Flight компіляції, effectiveAdrs з fallback |
| `src/components/CopilotPanel/CopilotStream.tsx` | Прибрано `setTimeout` симуляцію → `useCopilotStream()`. Додано Kill Stream кнопку + offline banner + streaming cursor |
| `src/components/ReviewGateModal.tsx` | Approve/Reject → `submitSprintReview()`. Додано панелі «Handoff dispatched» (approve) та «COW branch created» (reject) з copy-CLI кнопкою |
| `src/components/DrakonStudio/DrakonToolbar.tsx` | Додано prop `onSaveSpec` + prop `saveState: 'idle' | 'saving' | 'saved' | 'error'` + іконка з 4 станами |

### Не змінюй ці файли (я їх не чіпав, лишились як були у master cc5abc0)

- Усі інші компоненти (Topbar, PhaseStepper, InvariantDrawer, DrakonCanvas, NodeInspector, TokenGauge, ContextBadges, BitemporalRadar/*)
- `package.json` (усі потрібні deps вже там — `clsx`, `tailwind-merge`, `lucide-react`)
- `tsconfig.json` (працює з `noUnusedLocals: false`)
- Усі типи в `src/types/`
- Усі моки в `src/data/`
- `src/lib/utils.ts`, `src/lib/drakon/*`
- `tailwind.config.js`, `vite.config.ts`, `index.html`, `favicon.svg`, `drakonwidget.js`

---

## 13. Правила комунікації зі мною (frontend-агент)

- **Не переписуй те, що вже працює.** Мій `b-sdd-ui/` — живий контракт.
- **Не змінюй форму DTO без пояснення.** Якщо в `backend-types.ts` я маю `{ compiled_snapshot, word_count, max_budget }` — твоя відповідь МАЄ містити рівно ці поля. Додаткові — можеш, існуючі не перейменовуй.
- **Не забувай про Ukrainian labels.** Оператор україномовний. Технічні терміни залишаються англійськими (ADR, DRAKON, invariant, stream), допоміжні тексти українською.
- **Кожне рішення = ADR.** Нове рішення (напр. вибір формату CORS auth) → MADR у `b-sdd/docs/adr/`.
- **Дотримуйся B-SDD dogfooding.** Ти сам розробляєш workbench за тією методологією, яку він втілює.

---

## 14. Deadline та критерії приймання

- **Deadline:** визначає Head Architect (Volodymyr Kovalenko).
- **Definition of Done для Sprint N+2 (цей цикл):**
  - Всі 9 кроків тестового сценарію (§8) працюють end-to-end.
  - `docs/decision/PROMPT_FRONTEND_MIGRATION.md` створено з усіма 6 розділами §10.
  - §3 Astryx Adherence Confirmation заповнено.
  - CORS налаштовано для `http://localhost:5173`.
  - Файли з §12 закомічені у master.

---

## 15. Чекліст для Head Architect (перед видачею промту бекенду)

- [ ] **Цей файл (`HANDOFF_BACKEND.md`) закомічений у `b-sdd/docs/decision/`** — тоді бекенд-агент побачить його автоматично при читанні репо. (Один раз зробити copy-paste з Genspark → git add → git commit → git push.)
- [ ] У `.context/next_sprint.md` секції `## Cross-Component Directives` є рядок:
      `→ Read docs/decision/HANDOFF_BACKEND.md before starting Φ3 pre-flight compilation.`
      Це гарантує, що агент прочитає HANDOFF як частину свого стандартного вхідного контексту.
- [ ] Ти передав mTLS-сертифікати для `.251:9922` та `.184:18880`.
- [ ] Ти надав Appwrite `projectId` та service-account API-key (для майбутнього Ed25519).
- [ ] Ти повідомив бекенд-агента про Astryx-мандат (§11) — незалежно від того, чи має він Genspark-connector.
- [ ] Якщо у бекенд-агента **немає прямого доступу до Genspark project** `ab09b8da-...`, ти згенерував signed URLs або ZIP-архів `b-sdd-ui/` та передав його йому окремим повідомленням.

---

## 16. Джерела

- **b-sdd repo:** https://github.com/maxfraieho/b-sdd
- **DRAKON widget:** https://github.com/stepan-mitkin/drakonwidget
- **Astryx GitHub:** https://github.com/facebook/astryx
- **Astryx Storybook:** https://facebook.github.io/astryx/

---

**Слава роботі. Далі — твій хід. 🛡️**

**— Frontend Design Agent, Sprint N+2 (Phase 3 complete)**
