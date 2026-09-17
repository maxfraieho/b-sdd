# ПЛАН СПРИНТІВ УСУНЕННЯ ДЕФЕКТІВ ТА МОДЕРНІЗАЦІЇ B-SDD WORKBENCH

**Стандарт:** B-SDD Methodology & Multi-Session Handoff (ADR-001..ADR-012, ADR-FE-001)  
**База знань аудиту:** Джерело NotebookLM `"Аудит архітектури B-SDD UI"` (ID: `1766c3a7-3c45-4453-9d6b-e5cfda1b98c4`)  
**Принцип виконання:** Детермінований ланцюжок спринтів (Sprint Chaining per ADR-007) — кожен скрипт після валідації інваріантів та проходження шлюзів Φ1–Φ7 автоматично формує `.sh` команду наступного спринта.

---

## 1. Матриця розподілу дефектів за спринтами

| Спринт | Назва спринта | Дефекти з аудиту NotebookLM | Ключові інваріанти | Команда запуску | Наступний крок у ланцюжку |
|---|---|---|---|---|---|
| **Sprint 007** | **Drakon State Bridge & Visual Flow Parity** | **DEF-01** (Каталог пайплайнів порожній)<br>**DEF-02** (Розрив Canvas ↔ React state)<br>**DEF-03** (Pseudocode із застарілої схеми)<br>**INV-DR1** (Планарність та шампур) | **ADR-001-INV-01** (Spec as Single Source of Truth)<br>**ADR-008-INV-01** (Планарність $C = 0$ та шампур) | `./run_sprint_007.sh` | Генерує `run_sprint_008.sh` |
| **Sprint 008** | **Sovereign Backend Gateway & Copilot Streaming** | **DEF-05** (Моковий Copilot proxy)<br>**DEF-08** (Статичний 16-денний скрубер)<br>**DEF-09** (Mixed Content Cloudflare Pages) | **ADR-002-INV-01** (<50ms компіляція)<br>**ADR-004-INV-01** (Бітемпоральність $T_v/T_t$)<br>**ADR-005-INV-01** (Суверенний LLM Gateway) | `./run_sprint_008.sh` | Генерує `run_sprint_009.sh` |
| **Sprint 009** | **Cryptographic HITL Gate & Sovereign Git COW Branching** | **DEF-06** (Імітація COW-розгалуження)<br>**DEF-07** (Фіктивний підпис ed25519)<br>**INV-FE3** (Відсутність ErrorBoundary зон) | **ADR-007-INV-01** (WORM-ізоляція та COW)<br>**ADR-011-INV-01** (Ed25519 невідкличний підпис)<br>**FE-INV-03** (Ізоляція збоїв 4 зон) | `./run_sprint_009.sh` | Генерує `run_sprint_010.sh` |
| **Sprint 010** | **Astryx Design System Ergonomics & Mobile Parity** | **DEF-04** (Втрачений проп в MobileNav)<br>**INV-T1** (TokenGauge: слова vs токени)<br>**INV-FE1** (Паразитний скрол сторінки)<br>**INV-AST** (Залишки hex-кольорів Tailwind) | **FE-INV-01** (100vh no-body-scroll)<br>**FE-INV-02** (Токени Astryx `var(--*)`)<br>**ADR-FE-001** (Мобільний паритет) | `./run_sprint_010.sh` | Фінальний білд, деплой та WORM-коміт |

---

## 2. Детальні специфікації та кроки виконання спринтів

```
                                  ЛАНЦЮЖОК СПРИНТІВ B-SDD
  ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
  │   Sprint 007      │ ───► │   Sprint 008      │ ───► │   Sprint 009      │ ───► │   Sprint 010      │
  │ Drakon State      │      │ Sovereign LLM     │      │ Crypto HITL Gate  │      │ Astryx Ergonomics │
  │ Bridge & Catalog  │      │ Gateway & Streams │      │ & Git COW Branch  │      │ & Mobile Parity   │
  └───────────────────┘      └───────────────────┘      └───────────────────┘      └───────────────────┘
         │                          │                          │                          │
  генерує                    генерує                    генерує                    фіналізує
  run_sprint_008.sh          run_sprint_009.sh          run_sprint_010.sh          WORM ledger & CDN
```

### 2.1 Спринт 007: Drakon State Bridge & Visual Flow Parity
- **Мета:** Повне відновлення специфікації як єдиного джерела істини (ADR-001). З'єднання візуального маніпулятора `drakonwidget.js` із внутрішнім станом React `drakonNodes`, усунення мертвої кнопки в `PipelineCatalogModal`, динамічна генерація псевдокоду.
- **Фази B-SDD:**
  - **Φ1 (Intent):** Специфікація `specs/007-drakon-state-bridge-and-catalog/spec.md` (310 слів, <500 бюджет).
  - **Φ2 (DRAKON):** Планарна схема синхронізації подій віджета `drakonwidget.js` -> нормалізація в IR -> валідація $C = 0$ -> `setDrakonNodes`.
  - **Φ3 (TDD):** Тести `tests/test_drakon_bridge_and_catalog.py`:
    - Перевірка, що вибір будь-якого шаблону з каталогу повертає непорожній список валідних вузлів.
    - Перевірка, що мутація діаграми оновлює стан React і зберігається на сервер.
    - Перевірка, що `PseudocodeModal` транслює код з актуального стану.
  - **Φ4 (Code):**
    - `b-sdd-ui/src/lib/drakon/DrakonStateBridge.ts`
    - Оновлення `b-sdd-ui/src/components/PipelineCatalogModal.tsx` реальними шаблонами.
    - Оновлення `b-sdd-ui/src/App.tsx:handleDiagramChange` та передачі схеми в `PseudocodeModal`.
  - **Φ5 (Fitness):** 100% проходження тестів, ліміт слів <500, перевірка нульових перетинів $C = 0$.
  - **Φ6 (HITL):** Схвалення оператора на панелі шлюзу.
  - **Φ7 (Chaining):** Запис `.context/sprint_007_handoff.json` та створення `run_sprint_008.sh`.

---

### 2.2 Спринт 008: Sovereign Backend Gateway & Copilot Streaming
- **Мета:** Ліквідація мокового Copilot-стрімінгу (DEF-05), підключення локального шлюзу моделей `192.168.3.184:18880`, динамічний зчитувач бітемпоральної шкали з Git (DEF-08), та захищений транспортний шар (DEF-09).
- **Фази B-SDD:**
  - **Φ1 (Intent):** `specs/008-sovereign-copilot-and-gateway/spec.md` (290 слів).
  - **Φ2 (DRAKON):** Схема проксування SSE-потоку з ін'єкцією контекстів `[ADR]`, `[DRAKON]`, `[RULES]` та тайм-аутом 25с.
  - **Φ3 (TDD):** Тести `tests/test_sovereign_gateway_and_timeline.py`:
    - Тест підключення до `192.168.3.184:18880` через SSE.
    - Тест ендпоінту `/api/temporal/timeline` (парсинг реальних `git log`).
    - Тест обробки Mixed Content / Cloudflare fallback.
  - **Φ4 (Code):**
    - Реалізація в `src/server/workbench_server.py:handle_post_copilot_proxy` реального HTTP streaming клієнта.
    - Додавання `/api/temporal/timeline` у `workbench_server.py`.
    - Оновлення `b-sdd-ui/src/components/BitemporalRadar/TimelineSlider.tsx` для динамічного масштабування.
  - **Φ5 (Fitness):** Перевірка затримки компілятора правил <50ms (ADR-002), SLA шлюзу.
  - **Φ6 (HITL):** Схвалення оператора.
  - **Φ7 (Chaining):** Запис `.context/sprint_008_handoff.json` та генерація `run_sprint_009.sh`.

---

### 2.3 Спринт 009: Cryptographic HITL Gate & Sovereign Git COW Branching
- **Мета:** Юридична та архітектурна невідкличність рішень на Фазі Φ6 (DEF-06, DEF-07). Справжнє створення COW-гілки через `git checkout -b` при відхиленні; WebCrypto Ed25519 підпис маніфесту (RFC 8785); ізоляція 4 зон через `AstryxZoneBoundary` (INV-FE3).
- **Фази B-SDD:**
  - **Φ1 (Intent):** `specs/009-cryptographic-hitl-and-cow-branch/spec.md` (320 слів).
  - **Φ2 (DRAKON):** Алгоритм канонізації маніфесту -> підпис браузером -> перевірка бекендом -> створення підписаного Git-тегу або атомарне відгалуження COW.
  - **Φ3 (TDD):** Тести `tests/test_crypto_hitl_and_cow.py`:
    - Тест валідації Ed25519 підпису на бекенді через `cryptography`.
    - Тест фізичного створення гілки `cow/sprint-...` при Reject.
    - Тест працездатності `ErrorBoundary` при падінні Зони 2 (DRAKON Canvas).
  - **Φ4 (Code):**
    - `b-sdd-ui/src/lib/crypto/signer.ts` (WebCrypto API).
    - `b-sdd-ui/src/components/ReviewGateModal.tsx` (інтеграція реального підпису).
    - `src/server/workbench_server.py` (фізичний виклик `git checkout -b` та верифікація підпису).
    - `b-sdd-ui/src/components/boundaries/AstryxZoneBoundary.tsx`.
  - **Φ5 (Fitness):** Перевірка неможливості фальсифікації підпису, перевірка чинного робочого дерева Git.
  - **Φ6 (HITL):** Схвалення оператора із застосуванням реального ключа Ed25519.
  - **Φ7 (Chaining):** Запис `.context/sprint_009_handoff.json` та генерація `run_sprint_010.sh`.

---

### 2.4 Спринт 010: Astryx Design System Ergonomics & Responsive Mobile Parity
- **Мета:** Досягнення повної ергономічної відповідності стандарту Swiss High-Tech Dark (INV-AST, INV-FE1, INV-T1, DEF-04). Ліквідація подвійного скролу через `min-width: 0`, виправлення семантики `TokenGauge.tsx` (<500 слів за ADR-002), відновлення доступу до бібліотеки ADR на мобільних пристроях.
- **Фази B-SDD:**
  - **Φ1 (Intent):** `specs/010-astryx-ergonomics-and-mobile-parity/spec.md` (280 слів).
  - **Φ2 (DRAKON):** Алгоритм функціонального чергування контекстів для мобільних екранів та табличного вирівнювання чисел.
  - **Φ3 (TDD):** Тести `tests/test_astryx_ergonomics_and_mobile.py`:
    - Сканування коду на відсутність прямих кольорів `#XXXXXX` у `.tsx` (FE-INV-02).
    - Перевірка присутності кнопки ADR у `MobileNavigation.tsx`.
    - Перевірка розрахунку слів у `TokenGauge.tsx`.
  - **Φ4 (Code):**
    - `b-sdd-ui/src/components/MobileNavigation.tsx` (деструктуризація `onOpenAdrLibrary`).
    - `b-sdd-ui/src/components/CopilotPanel/TokenGauge.tsx` (розмежування слів і токенів).
    - `b-sdd-ui/src/index.css` та компоненти `src/components/astryx/primitives.tsx`.
    - Складання оновленого продакшн-бандлу `npm run build`.
  - **Φ5 (Fitness):** Фінальний аудит кодової бази: `FE-INV-01`, `FE-INV-02`, `A001..A012`.
  - **Φ6 (HITL):** Фінальний підпис Head Architect.
  - **Φ7 (Handoff):** Запис у сховище Utopia DB, деплой на Cloudflare Pages (`https://b-sdd-ui.pages.dev`).
