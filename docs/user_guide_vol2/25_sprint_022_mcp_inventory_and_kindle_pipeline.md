# Спринт 022: Інвентаризація MCP-серверів, вочдог n8n та пайплайн Kindle

**Sprint ID:** `sprint_022`  
**Статус:** Успішно завершено  
**Основні інваріанти:** ADR-011, ADR-012, Invariant FL-01

---

## 1. Мета та архітектурний фокус
Повна каталогізація підключених інструментів Model Context Protocol (MCP), розробка системного наглядача (watchdog) для n8n воркфлоу оркестрації та інтеграція пайплайну доставки документації на пристрої Amazon Kindle.

## 2. Ключові досягнення
- **MCP Inventory & Capabilities:** Створено вичерпний маніфест `docs/MCP_SERVERS_AND_CAPABILITIES.md` (NotebookLM, GitNexus, n8n, Utopia, SQLite).
- **n8n Watchdog (`scripts/n8n_watchdog.py`):** Забезпечено постійний моніторинг виконання та автоматичний перезапуск завислих воркфлоу.
- **Kindle Documentation Pipeline:** Інтегровано модуль генерації EPUB 3.0 та відправки через Gmail API OAuth2 на `tukroschu@kindle.com`.
- **Direct Telegram Fallback:** Додано пряме резервне сповіщення оператора у разі недоступності зовнішніх вебхуків.
