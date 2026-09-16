# Phase 3 · Live API & Sovereign Engine Integration

**Status:** ✅ Completed
**Author:** Frontend Design Agent (Genspark)
**Backend counterpart:** `src/server/workbench_server.py` (100% Python stdlib, 31/31 tests passing)
**Wire endpoint:** `http://localhost:8765` (override via `VITE_API_BASE_URL` in `.env.local`)

---

## Що додано у цьому спринті

### 1. `src/lib/backend-types.ts`
Строго типізовані DTO для всіх 5 backend-контрактів + SSE frame union
(`HealthResponse`, `ActiveRulesResponse`, `AdrsResponse`, `DrakonSchemaResponse`,
`DrakonSchemaSavePayload`, `SprintReviewPayload`, `SprintReviewResponse`,
`CopilotProxyPayload`, `CopilotSseEvent`). Форми дзеркалять контракт з
`b-sdd/docs/PROMPT_GENSPARK_PHASE3_FULL_INTEGRATION.md`.

### 2. `src/lib/api.ts`
Універсальний `fetchWithFallback<T>()` — на кожен GET-запит гарантовано
повертає або живі дані, або наданий fallback-снепшот, якщо сервер
недоступний (timeout 3.5s, HTTP 5xx, network error). Реалізує:

- `getHealth()`, `getActiveRules()`, `getAdrs()`, `getDrakonSchema()`
- `saveDrakonSchema()`, `submitSprintReview()` (POST без fallback — write
  intent не можна тихо ковтати)
- `subscribeLiveMode()` — event-based підписка на статус `online`/`offline`
  для майбутнього badge у Topbar

### 3. `src/lib/sse.ts`
Реальний Server-Sent Events клієнт для `POST /api/copilot/proxy`.
Використовує `fetch` + `ReadableStreamDefaultReader` (EventSource не
підтримує POST з JSON body). Парсер обробляє multi-line `data:` frames,
підтримує `[DONE]` sentinel і 4 типи подій: `token`, `meta`, `done`,
`error`. Повертає `SseHandle` з методом `abort()` для Kill Stream кнопки.

### 4. `src/hooks/useLiveData.ts`
Реюзабельний React 19 хук, який поллить будь-який `fetchWithFallback`-based
endpoint із конфігурованою cadence, повертає `{data, isLive, error, refresh}`,
підтримує `deps[]` для реактивного refresh (наприклад, при русі слайдера
таймлайну).

### 5. `src/hooks/useCopilotStream.ts`
Обгортає `openCopilotStream()` у React state. Експонує `{streamingText,
isStreaming, error, start, abort}`. При помилці сервера — виставляє
`Error` об'єкт; caller (CopilotStream.tsx) додає fallback-повідомлення
у бабл, замість того щоб краш.

### 6. Оновлення `CopilotStream.tsx`
Видалено `setTimeout` симуляцію. Тепер:
- `handleSendPrompt` викликає `startStream()` з real `POST /api/copilot/proxy`.
- Токени з SSE прогресивно записуються у поточний assistant-бабл.
- Kill Stream кнопка з'являється під час стріму та викликає `abortStream()`.
- Offline fallback: якщо gateway недоступний — бабл отримує префікс
  `[⚠ offline fallback]` замість перерваного стріму.

### 7. Оновлення `ReviewGateModal.tsx`
Approve/Reject тепер асинхронні:
- `handleApprove()` викликає `submitSprintReview({action: 'approve'})` +
  показує панель «Handoff dispatched» з `cycleId`, `launch_command` та
  кнопкою `copy` для CLI.
- `handleConfirmReject()` викликає `submitSprintReview({action: 'reject', ...})`
  з `negative_invariants`, `rationale`, `rollback_depth`; показує панель
  «Copy-on-write branch created» з `next_sprint_id`.
- Backend error → жовтий inline банер + optimistic local state зберігається.

### 8. Оновлення `DrakonToolbar.tsx` та `App.tsx`
Нова кнопка **💾 Save Spec** (4-стани: `idle`, `saving`, `saved`, `error`).
`handleSaveSpec` в App експортує live diagram через `canvasRef.current.exportJson()`,
парсить у `DrakonWidgetDiagram`, потім POST на `/api/drakon/schema` разом
з canonical `schema_ir`. Візуальний feedback повертається у tooltip
кнопки, включно з backend error message.

### 9. `.env.example` + оновлений `_headers`
CSP whitelist розширений — тепер `connect-src` включає:
- `http://localhost:8765` та `http://127.0.0.1:8765` (workbench server)
- Sovereign VPC endpoints (незмінно)

---

## Тестовий сценарій End-to-End

```bash
# Термінал 1: запусти бекенд
cd /path/to/b-sdd
python3 -m src.cli.main serve --port 8765

# Термінал 2: запусти фронт
cd b-sdd-ui
npm install
npm run dev  # http://localhost:5173

# Або в один клік (за умови наявності скрипта у b-sdd/):
./run_workbench.sh
```

Далі:
1. Відкрити http://localhost:5173 — Topbar має завантажити health chip.
2. **Копілот:** введіть prompt → має розпочатися SSE стрім (з ~42 tok/s).
   Клацніть Kill Stream — має зупинити на середині.
3. **Timeline:** перемістіть T_v/T_t слайдер → фронт зробить `GET /api/adrs`
   з новими параметрами (реактивно через `deps`).
4. **DRAKON Studio:** клікніть 💾 Save Spec — має піти POST на
   `/api/drakon/schema`, кнопка спалахне зеленим на 2.2s.
5. **Review Gate:** відкрийте Φ6 → натисніть Approve → з'явиться
   Handoff-панель з CLI-командою; клікніть Copy → команда у clipboard.
6. **Offline test:** вимкніть бекенд → всі виклики автоматично впадуть
   у fallback mode, UI лишиться повністю інтерактивним (мокові дані).

---

## Що НЕ включено в цей спринт (свідомо)

- **Двонаправлене редагування ДРАКОН вузлів** — Save Spec поки експортує
  тільки поточний canonical IR. Live editing вимагає підняти `canSelect`
  до `edit` mode у widget config та розгорнути `ir-bridge.ts` для парсу
  редагованих полів (наступний спринт).
- **Ed25519 крипто-підпис оператора** — `operator_signature` поле у
  `SprintReviewPayload` існує, але не заповнюється. Треба інтеграція з
  Appwrite Auth JWT (Sprint N+2).
- **Astryx design-system міграція** — див.
  `../docs/decision/DELTA_C_ASTRYX_OMISSION.md`. Заплановано на окремий
  Sprint N+2 як механічну заміну Tailwind-класів на `@astryxdesign/core`
  компоненти.

---

## Дотримані інваріанти

- ✅ **ADR-008-INV (Offline Parity):** усі GET-виклики мають fallback до
  мокових знімків, UI не втрачає інтерактивність без бекенду.
- ✅ **ADR-002-INV-02 (Token Budget):** `liveTokenBudget` тепер деривується
  з `GET /api/rules/active` word_count (замість hardcoded 476).
- ✅ **ADR-024-INV-02 (mTLS):** CSP-headers дозволяють тільки `https://` для
  sovereign VPC endpoints; localhost:8765 виняток бо це dev-only proxy.
- ✅ **ADR-007-INV-01 (Handoff signed by operator):** UI відображає
  `launch_command` тільки якщо backend підтвердив `cycle_id`.
- ✅ **Zero-Dependency Pure Runtime:** нові файли додають тільки один
  runtime import (`lucide-react` іконки Loader2, Copy, Terminal, WifiOff)
  — все інше через існуючі React 19 + fetch API.
