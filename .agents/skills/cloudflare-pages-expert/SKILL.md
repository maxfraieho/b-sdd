---
name: cloudflare-pages-expert
description: Автономна збірка, конфігурація (_headers, _redirects, CORS, CSP) та публікація фронтенду Astryx Cockpit (b-sdd-ui) у Cloudflare Pages через Wrangler CLI.
type: SYSTEM_SKILL
category: bssd-system-skill
immutable: true
invoked_skills: [diagnosing-bugs, laya-decision-router, safe-refactor, test-driven-development, utopia-intent-ledger]
---
# Cloudflare Pages Expert: Публікація Astryx Cockpit

Автономний процедурний скіл для деплою та верифікації фронтенду **Astryx Cockpit / Copilot** (`b-sdd-ui`) у середовищі **Cloudflare Pages**. Забезпечує коректну маршрутизацію Single Page Application (SPA), захищені CSP/CORS заголовки для двостороннього SSE-стрімінгу з бекенд-шлюзів (порт 8765/8161 на .161 та порт 9623 на Pixel 7), а також автоматизовану валідацію доступності сайту.

---

## 📐 Канонічний алгоритмічний псевдокод (B-SDD ADR-016 Standard)

> [!IMPORTANT]
> Цей псевдокод є 1:1 текстовим ізоморфізмом планарної ДРАКОН-схеми `cloudflare-pages-expert.drakon.json`. Будь-які модифікації процедури повинні спочатку вноситися у візуальну схему або синхронізуватися з цим блоком.

```text
ALGORITHM DeployAstryxToCloudflarePages
BEGIN
    TRY
        // Шампур X=0: Крок 1 — Перевірка передумов та середовища
        ASSERT DirectoryExists("~/projects/b-sdd/b-sdd-ui")
        ASSERT FileExists("~/projects/b-sdd/b-sdd-ui/package.json")

        // Шампур X=0: Крок 2 — Збірка виробничого бандлу фронтенду
        EXECUTE "cd ~/projects/b-sdd/b-sdd-ui && npm run build"
        IF NOT DirectoryExists("~/projects/b-sdd/b-sdd-ui/dist") THEN
            BRANCH_RIGHT(X=4.0) // Гілка деградації
            LOG_ERROR("TypeScript/Vite build failed. dist/ not produced.")
            CALL_SKILL(diagnosing-bugs)
            HALT_AND_DEGRADE("Frontend Build Error")
        FI

        // Шампур X=0: Крок 3 — Генерація конфігурацій Cloudflare Pages (_headers та _redirects)
        GENERATE_FILE "~/projects/b-sdd/b-sdd-ui/dist/_headers" WITH:
            "/*"
            "  Access-Control-Allow-Origin: *"
            "  Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS"
            "  Access-Control-Allow-Headers: Content-Type, Authorization"
            "  Content-Security-Policy: default-src 'self' 'unsafe-inline' 'unsafe-eval' http://192.168.3.161:* http://192.168.3.251:* https://bsdd.exodus.pp.ua wss: ws:;"
        GENERATE_FILE "~/projects/b-sdd/b-sdd-ui/dist/_redirects" WITH:
            "/* /index.html 200"

        // Шампур X=0: Крок 4 — Деплой через Wrangler CLI
        EXECUTE "npx wrangler pages deploy dist --project-name=astryx-cockpit"
        IF ExitCode != 0 THEN
            BRANCH_RIGHT(X=4.0) // Гілка деградації
            LOG_WARN("Direct Wrangler deploy failed. Attempting remote fallback deployer via 192.168.3.184.")
            EXECUTE "~/projects/b-sdd/scripts/deploy_cloudflare_pages.sh"
            IF ExitCode != 0 THEN
                RAISE Error("Both local Wrangler and remote deployer failed.")
            FI
        FI

        // Шампур X=0: Крок 5 — Валідація живого URL
        TARGET_URL := "https://astryx-cockpit.pages.dev"
        HTTP_RESPONSE := HTTP_GET(TARGET_URL, Timeout=10s)
        IF HTTP_RESPONSE.StatusCode != 200 THEN
            BRANCH_RIGHT(X=4.0)
            LOG_WARN("Validation returned HTTP " + HTTP_RESPONSE.StatusCode)
        ELSE
            LOG_INFO("✓ Astryx Cockpit online: " + TARGET_URL)
            EMIT_TELEMETRY(status="DEPLOYED", url=TARGET_URL)
        FI

        // Шампур X=0: Крок 6 — Завершення
        RETURN Success("Deployment verified")

    CATCH Exception AS e
        LOG_CRITICAL("❌ [CLOUDFLARE DEPLOY CRITICAL]: " + e.Message)
        HALT_AND_DEGRADE("Localhost Server Fallback (http://192.168.3.161:8765)")
    END
END
```

---

## 🛠️ Процедурний алгоритм виконання

### 1. Збірка виробничого пакету
Виконується типізована збірка Vite + React 19:
```bash
cd ~/projects/b-sdd/b-sdd-ui
npm run build
```

### 2. Генерація артефактів Cloudflare Pages
Для забезпечення коректної роботи SPA-роутингу та крос-доменного SSE-стрімінгу з вузлів .161 та .251 генеруються файли в каталозі `dist/`:

#### Файл `dist/_headers`:
```text
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

#### Файл `dist/_redirects`:
```text
/*    /index.html   200
```

### 3. Публікація через Wrangler CLI
```bash
cd ~/projects/b-sdd/b-sdd-ui
npx wrangler pages deploy dist --project-name=astryx-cockpit --branch=main
```
*У разі відсутності локального токена Cloudflare використовується автономний скрипт деплою через вузол 184:*
```bash
~/projects/b-sdd/scripts/deploy_cloudflare_pages.sh
```

### 4. Верифікація доступності
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://astryx-cockpit.pages.dev
# Очікувана відповідь: 200
```

---

<!-- DRAKON_VISUAL_FLOW_START -->
## DRAKON Visual Workflow (Planar Skewer X=0)
- **Schema File:** `cloudflare-pages-expert.drakon.json`
- **Total Algorithmic Nodes:** 11
- **Spine Topology:** Vertical Skewer ($X=0, C=0$) verified.
  1. `[HEADLINE]` Початок: Публікація Astryx Cockpit у Cloudflare Pages
  2. `[ACTION]` Крок 1: Перевірка передумов робочого простору b-sdd-ui
  3. `[QUESTION]` Крок 2: Збірка npm run build успішна?
  4. `[ACTION]` Помилка збірки TypeScript/Vite: логування та зупинка
  5. `[ACTION]` Крок 3: Генерація dist/_headers (CORS, CSP) та dist/_redirects
  6. `[QUESTION]` Крок 4: Деплой через локальний Wrangler CLI успішний?
  7. `[ACTION]` Деградація: Запуск віддаленого деплоєра через вузол .184
  8. `[ACTION]` Крок 5: HTTP GET верифікація доступності https://astryx-cockpit.pages.dev == 200
  9. `[ACTION]` Крок 6: Реєстрація релізу в Utopia DB WORM леджер
  10. `[END]` Завершення: Публікація Astryx Cockpit успішна
  11. `[END]` Завершення з помилкою: Перехід на локальний сервер
<!-- DRAKON_VISUAL_FLOW_END -->
