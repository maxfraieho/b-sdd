# Genspark Code Master Prompt: B-SDD Operator Workbench (Phase 2: Full Code & Production Build)
## Перехід від пілотного дизайну до повноцінного React/Vite проекту для Cloudflare Pages

---

### 1. МЕТА ТА КОНТЕКСТ
Пілотний дизайн успішно верифіковано в Genspark Design. Тепер необхідно згенерувати повноцінний проект **Vite + React 19 + TypeScript + Tailwind CSS** (`b-sdd-ui`), який:
1. Повністю зберігає узгоджену 4-зональну топологію та колірні токени Swiss High-Tech (`#070B12`, `#0D1424`, `#162035`, `#24324D`).
2. Інтегрується з ядром B-SDD: схемою ДРАКОН (`DRAKON-IR`), бітемпоральними ADR та суверенними шлюзами (`.251:9922` Utopia DB, `.184:18880` LLM Gateway).
3. Збирається в один клік (`npm run build`) у папку `dist/` для негайного деплою на **Cloudflare Pages**.

---

### 2. СТРУКТУРА КОМПОНЕНТІВ ПРОЕКТУ

```
b-sdd-ui/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── public/
│   ├── _headers                  # Cloudflare security headers & CSP
│   ├── _redirects                # SPA routing: /* /index.html 200
│   └── favicon.svg
├── src/
│   ├── index.css                 # Swiss Dark CSS variables & Tailwind directives
│   ├── main.tsx
│   ├── App.tsx                   # 4-zone spatial grid layout
│   ├── types/
│   │   ├── adr.ts                # Bitemporal ADR model (T_v, T_t, status)
│   │   ├── drakon.ts             # DRAKON-IR (headline, action, question, edges)
│   │   ├── sprint.ts             # HITL Phase Phi_1 - Phi_7 state machine
│   │   └── copilot.ts            # LLM slots & SSE streaming types
│   ├── components/
│   │   ├── Topbar.tsx            # Project switcher, node health, tier badge
│   │   ├── PhaseStepper.tsx      # Interactive 7-phase stepper (Phi_1 - Phi_7)
│   │   ├── ReviewGateModal.tsx   # Blocking Phi_6 Human Review Gate & Reject dialog
│   │   ├── DrakonStudio/
│   │   │   ├── DrakonCanvas.tsx  # SVG/Canvas renderer (skewer, right branches)
│   │   │   ├── DrakonNode.tsx    # Icons: Headline, Action, Question, End
│   │   │   └── NodeInspector.tsx # Slide-out drawer with ADR invariant binding
│   │   ├── CopilotPanel/
│   │   │   ├── CopilotStream.tsx # Token streaming simulation & slot selector
│   │   │   ├── TokenGauge.tsx    # 500-word pre-flight budget gauge
│   │   │   └── ContextBadges.tsx # Attach Active ADR / Attach DRAKON buttons
│   │   ├── BitemporalRadar/
│   │   │   ├── TimelineSlider.tsx# Dual-axis sliders (T_v valid, T_t transaction)
│   │   │   └── AdrListCard.tsx   # Supersession visualization (ADR-008 -> ADR-013)
│   │   └── InvariantDrawer.tsx   # Slide-out 420px drawer with Tantivy search mock
│   └── data/
│       ├── mockAdrs.ts           # 8 realistic MADR decisions with bitemporal dates
│       ├── mockDrakonSchema.ts   # Canonical 7-phase HITL pipeline DRAKON-IR
│       └── mockSprints.ts        # Sprint status and delta-C negative invariant vectors
```

---

### 3. КЛЮЧОВІ ІНТЕРАКТИВНІ СЦЕНАРІЇ ДЛЯ РЕАЛІЗАЦІЇ

1. **Степпер фаз $\Phi_1 - \Phi_7$:**
   - Перемикання фаз динамічно змінює стан кокпіта.
   - При активації $\Phi_6$ блокується екран і виводиться плашка **Human Review Gate** з фітнес-метриками (`25/25 tests passed`, `AST Isolation: 100%`) та двома діями:
     - `[ 🛡️ Затвердити та підписати (Approve) ]` -> перехід до $\Phi_7$ (Handoff).
     - `[ ❌ Відхилити та розгалузити (Reject & Branch) ]` -> модальне вікно вибору глибини відкату та ін'єкції вектора $\Delta C$.

2. **Студія ДРАКОН (Drakon-as-Spec Canvas):**
   - Рендеринг схеми із строго вертикальним лівим шампуром ($x=0$) та відгалуженнями деградації праворуч ($x > 0$).
   - Клік на вузол відкриває **Node Inspector** із прив'язаним `adr_invariant_id` (наприклад, `ADR-008: DRAKON Visual Logic`).
   - Відсутність перетину ліній (планарний граф).

3. **Бітемпоральний таймлайн ADR ($T_v / T_t$):**
   - Переміщення слайдера валідного часу ($T_v$) динамічно підсвічує активні ADR зеленим кольором, а застарілі/суперседовані — закреслює та переводить у сірий стан з посиланням на замінююче рішення.

4. **ШІ-Копілот:**
   - Перемикач 8 слотів моделей (`agent-proxy:18880`, `coding-proxy:18880`, `reasoning-proxy:8082`).
   - Індикатор заповнення токен-бюджету (ліміт: 500 слів для активних правил).
   - Кнопка запуску симуляції стрімінгу коду.

---

### 4. ТЕХНІЧНІ ВИМОГИ ДО КОДУ ТА ЗБІРКИ
- Чистий TypeScript без `any`.
- Іконки: `lucide-react`.
- Безпека стилів: Tailwind CSS 3.4+ з конфігурацією темної теми.
- Робота 100% offline на мокових даних без помилок за відсутності мережі.
- Успішна компіляція `npm run build` без попереджень TypeScript.
