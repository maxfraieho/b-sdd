# Вхідні Дані Ремедіації Інтерфейсу (Sprint 011 Intake)
**Джерело:** Дослідження в NotebookLM ("B-SDD Methodology, Multi-Session Handoff & Architecture") та промпт Gemini [`docs/ui_remediation/gemini-code-1789716881486.md`](file:///home/vokov/projects/b-sdd/docs/ui_remediation/gemini-code-1789716881486.md).
**Дата фіксації:** 2026-09-18

---

## 1. Дефекти для Термінового Виправлення (P0 / P1 Bugs)

- [x] **BUG-01 (Zone D CSS Overlap):** Накладання плашки часу $T_v$ / $T_t$ поверх карток ADR у `TimelineSlider.tsx`.
  - *Фікс:* Жорсткий flex-розподіл: ліва закріплена колонка часу (`w-72 flex-shrink-0 border-r border-border-subtle bg-surface-dark`) та скрол-контейнер карток (`flex-1 overflow-x-auto`).
- [x] **BUG-02 (Drakon Node Editor Mutation Disconnect):** Клік «Застосувати зміни» в інспекторі вузла не оновлює схему на канвасі `drakonwidget.js`.
  - *Фікс:* Викликати `drakonWidgetRef.current.setContent(nodeId, newText)`, оновити `items[nodeId]` у сховищі Zustand (`useDiagramStore`), викликати `drakon.redraw()` та виконати дебаунс-запит `POST /api/drakon/save`.
- [x] **BUG-03 (Project Switcher No-Op):** Кнопка «Вибрати» в `ProjectSwitcherModal` не перемикає активний репозиторій.
  - *Фікс:* Підключити до бекенд-ендпоінту `POST /api/projects/switch { project_id }`, оновити робочий каталог, пересканувати `.context/active_rules.md`, `specs/` та інвалідувати кеш у клієнті.
- [x] **BUG-04 (ADR Read-Only Lock):** Бібліотека ADR працює виключно як статичний переглядач.
  - *Фікс:* Додати інлайн-редагування MADR 3.0, кнопку «+ Новий ADR» (для фази Φ1) та підключити збереження через `POST /api/adrs` з генерацією транзакції суперсесії в Utopia DB (`.251:9922`).

---

## 2. Нові Можливості та Ергономіка (Astryx v2 & Genspark)

- [x] **FEAT-01 (Full Drakon Palette & Grouped Tooling):** Збереження всіх 20+ фігур мови ДРАКОН (обрізання до 5 фігур скасовано!).
  - *Фікс:* Організація палітри у 4 компактні сегментовані вкладки Astryx:
    1. `Flow Primitives`: header/b0, action, end, insertion.
    2. `Branching & Decisions`: question, case, select.
    3. `Loops & Iterations`: loop_start, loop_end, for-begin, for-end.
    4. `Real-time & System`: timer, pause, concurrent_process, address, comment.
- [x] **FEAT-02 (Drakon Dual-Mode: Structure vs Logic):** Підтримка перемикання між алгоритмічною логікою (`logic.drakon.json`) та структурною декомпозицією (`structure.drakon.json`) на базі нотації ERIL / Силует.
  - *Фікс:* Вмонтувати двопозиційний перемикач `[ Логіка (Flow) | Структура (Structure) ]` у `DrakonToolbar.tsx`.
- [x] **FEAT-03 (Utopia DB DAG View у Зоні D):** Візуалізація графа залежностей рішень над таймлайном.
  - *Фікс:* Перемикач `[ Картки ADR | Бітемпоральний Граф Utopia ]` з відображенням ребер `supersedes`, `depends-on`, `conflicts-with` та фільтрацією застарілих рішень при русі слайдера $T_v$.

---

## 3. Розташування Компонентів та Дизайн-Артефактів:
1. **Готові компоненти Astryx v2 від Genspark:**
   - `/home/vokov/projects/swiss-job-hunter/docs/RESULTS_RESORCH/resesign/design_handoff_bsdd_workbench_astryx_v2`
   - `/home/vokov/projects/b-sdd/docs/redecisijn/design_handoff_bsdd_workbench_astryx_v2`
2. **Зрілі UI-компоненти:**
   - `192.168.3.184:/home/vokov/projects/garden-seedling-stage` (`DrakonEditor.tsx`, `MemoryPanel.tsx`, `RevisionSnapshotViewer.tsx`, `ZoneNotebookLMChat.tsx`).
3. **Промпт запуску сесії:**
   - [`docs/ui_remediation/gemini-code-1789716881486.md`](file:///home/vokov/projects/b-sdd/docs/ui_remediation/gemini-code-1789716881486.md).
