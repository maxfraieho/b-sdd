# Genspark Master Prompt: B-SDD Operator Workbench (Phase 3: Live API & Sovereign Engine Integration)
## Інтеграція інтерфейсу `b-sdd-ui` з локальним бекендом B-SDD, бітемпоральним SQLite-кешем та суверенними шлюзами

---

### 1. КОНТЕКСТ ТА ПОТОЧНИЙ СТАН
Проєкт `b-sdd-ui` успішно зібрано на базі **Vite + React 19 + TypeScript + Tailwind CSS** із інтеграцією канонічного рушія **DrakonWidget** від Степана Мітькіна (`/libs/drakonwidget.js`).
Створено:
- 4-зональну топологію: Топбар (48px), Фазовий степпер $\Phi_1 - \Phi_7$ (64px), Студія ДРАКОН (55%), Панель ШІ-Копілота (45%) та Бітемпоральний радар (135px).
- Модальне вікно блокуючого шлюзу $\Phi_6$ (Human Review Gate) із підтримкою протоколу **Reject & Branch** та криптографічного підпису.
- Інспектор вузлів (Node Inspector) та бічний слайдер інваріантів Utopia DB (Invariant Drawer).

**Мета Фази 3:** Перевести `b-sdd-ui` з мокових даних на живе двостороннє спілкування з локальним сервером B-SDD (`http://localhost:8765`) та суверенними шлюзами:
1. `GET /api/rules/active` — відображення живого скомпільованого знімка активних правил та токен-бюджету (<500 слів).
2. `GET /api/adrs` — динамічне оновлення графа рішень відповідно до положення повзунків $T_v$ та $T_t$.
3. `GET /api/drakon/schema` та `POST /api/drakon/schema` — двостороння синхронізація схеми алгоритму з файлами `specs/**/logic.drakon.json`.
4. `POST /api/sprint/review` — відправка рішення оператора (Approve / Reject & Branch) та автоматичний запуск наступного спринту через CLI.
5. `POST /api/copilot/proxy` — повноцінний SSE-стрімінг коду безпосередньо з LLM Gateway (`.184:18880`).

---

### 2. КЛЮЧОВІ ІНТЕГРАЦІЙНІ МОДУЛІ ДЛЯ РЕАЛІЗАЦІЇ В `b-sdd-ui`

#### 2.1 API Клієнт із автоматичним перемиканням у режим Offline Parity (`src/lib/api.ts`)
```typescript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8765';

export async function fetchWithFallback<T>(endpoint: string, fallbackData: T): Promise<T> {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`[API Offline Fallback] Using local snapshot for ${endpoint}`, err);
    return fallbackData;
  }
}
```

#### 2.2 Live SSE Стрімінг для Копілота (`src/lib/sse.ts`)
Підключення до `POST /api/copilot/proxy` з підтримкою чанкового читання через `ReadableStreamDefaultReader` та виведенням токенів у режимі реального часу.

#### 2.3 Двостороння синхронізація ДРАКОН (`src/components/DrakonStudio/`)
- При внесенні змін оператором у вузол (наприклад, редагування назви або прив'язки `adr_invariant_id`), генерувати оновлений `DRAKON-IR` через `convertDrakonDiagramToIr()`.
- Кнопка `[ 💾 Save Spec ]` зберігає оновлену схему у `specs/004-multi-session-handoff-and-drakon/logic.drakon.json` через POST-запит.

#### 2.4 Запуск наступного спринту в один клік (`src/components/ReviewGateModal.tsx`)
Після натискання `[ 🛡️ Approve & Cryptographically Sign ]`:
- Викликати `POST /api/sprint/review` з payload `{ action: 'approve', sprint_id: '...' }`.
- Сервер генерує `.context/sprint_handoff.json` та повертає готову команду запуску:
  `./run_b_sdd.sh --auto-chain`
- Інтерфейс виводить сповіщення про готовність естафети та відображає прогрес запуску наступного спринту.

---

### 3. ІНСТРУКЦІЯ ЗБІРКИ ТА ПЕРЕВІРКИ
1. Перевірити типи: `npm run build` (повинно збиратися без помилок).
2. Запустити локальний сервер розробки: `npm run dev`.
3. Забезпечити працездатність як при підключеному бекенді (`localhost:8765`), так і при повністю автономному (offline) режимі на вбудованих знімках даних.
