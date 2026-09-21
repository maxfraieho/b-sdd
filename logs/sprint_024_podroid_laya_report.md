# INBOX_GEMINI_SPRINT_024_PODROID_LAYA_REPORT

## 1. Executive Summary & Context
- **Sprint:** `sprint_024`
- **Directive:** `OUTBOX_AGI_SPRINT_024_PODROID_LAYA_WATCHDOG`
- **Correlation ID:** `corr_20260921_podroid_01`
- **Primary Host:** `100.65.225.122` / `192.168.3.161` (`~/projects/b-sdd`)
- **Edge Node:** Google Pixel 7 (Podroid Alpine VM: `192.168.3.251`)
- **Architecture Invariant:** Pure Python Standard Library (ADR-002), Zero-RAM Overhead on Host .161, Invariant FL-01 Closed-Loop Delivery.

---

## 2. Problem Statement & Resolution
On Host .161, resident memory pressure is severe (free RAM regularly drops to ~42MB). Running a resident 322M-parameter model on Host .161 presents an unacceptable risk of OOM kills.

### Offloading Strategy:
- **Compute Offload:** The non-autoregressive System 1 decision engine (Laya: mmBERT-base 322M) has been offloaded to Google Pixel 7 running Podroid (Alpine Linux VM with 4GB RAM, 4 vCPUs, 32GB storage) on LAN IP `192.168.3.251`.
- **Sub-40ms Guarantee:** Laya daemon processes `/predict` queries in under 40ms, returning binary and categorical decisions with confidence ratings.
- **Sovereign Watchdog:** Android OS power management may suspend background VM execution. A dedicated watchdog daemon and timer on Host .161 continuously verifies ports 9622 (Utopia DB) and 9623 (Laya REST daemon) and dispatches immediate Telegram alerts when downtime is detected, prompting the operator for manual tap-restart.

---

## 3. Implemented Deliverables

### Deliverable A: Laya Daemon Setup Package for Podroid (`deploy/podroid/`)
1. **`deploy/podroid/laya_daemon.py`**:
   - High-performance, lightweight HTTP server listening on `0.0.0.0:9623`.
   - `GET /health`: Returns service metadata, runtime arch, and model information.
   - `POST /predict`: Receives `{state, questions}` and produces sub-40ms System 1 decisions.
   - Standard library-based with optional ONNX runtime acceleration (`onnxruntime`).
2. **`deploy/podroid/setup_laya_alpine.sh`**:
   - Automated setup script for Alpine Linux inside Podroid (`apk add python3 py3-pip gcompat ...`).
   - Prepares `/opt/laya`, installs runtime, sets up OpenRC service.
3. **`deploy/podroid/podroid_laya.service` & `deploy/podroid/podroid_laya.initd`**:
   - Systemd unit and Alpine OpenRC init script (`rc-service podroid-laya start`).
4. **`deploy/podroid/start_laya.sh`**:
   - Standalone background runner with PID tracking and logging to `/var/log/laya/laya.log`.
5. **`deploy/podroid/README.md`**:
   - Comprehensive operator deployment and verification guide.

### Deliverable B: Podroid Sovereign Watchdog on Host .161 (`scripts/podroid_watchdog.py`)
1. **`scripts/podroid_watchdog.py`**:
   - Socket connection monitor for Utopia DB (`192.168.3.251:9622`).
   - HTTP health check for Laya Decision Engine (`http://192.168.3.251:9623/health`).
   - State caching in `/tmp/podroid_watchdog_state.json` to prevent alert fatigue.
   - Telegram notifications using Bot `8717667434` to Chat `6412868393`.
   - Formats exact Ukrainian alert and recovery messages:
     - Downtime: `🚨 [ALERT: B-SDD PODROID DOWNTIME] Podroid на Pixel 7 (192.168.3.251) вимкнено!`
     - Recovery: `🟢 [RECOVERED: B-SDD PODROID] Podroid на Pixel 7 успішно відновив роботу (Utopia DB: 9622, Laya: 9623).`
2. **`systemd/b-sdd-podroid-watchdog.service` & `systemd/b-sdd-podroid-watchdog.timer`**:
   - Systemd timer running watchdog checks every 2 minutes (`OnUnitActiveSec=2min`).

### Deliverable C: B-SDD Core Client Hook (`src/core/laya_client.py`)
1. **`src/core/laya_client.py`**:
   - Zero-dependency client using `urllib.request`. Zero RAM footprint on Host .161.
   - Method `query_decision(state, questions, timeout=3.0) -> dict`.
   - **Graceful Degradation:** If Pixel 7 / Podroid is suspended or unreachable, returns `fallback: True` with a safe heuristic decision without raising unhandled exceptions or crashing the supervisor.
   - Method `check_health() -> dict` for quick diagnostics.

---

## 4. Test Verification & Architectural Fitness
- **Sprint 024 Unit Tests:**
  - `tests/test_laya_client.py`: 8/8 PASSED.
  - `tests/test_podroid_watchdog.py`: 7/7 PASSED.
- **Regression Suite:**
  - `tests/test_tripartite_adr.py`: 7/7 PASSED.
  - `tests/test_planar_solver.py`: 6/6 PASSED.
  - `tests/test_architecture_fitness.py`: 5/5 PASSED.
  - **Total Required Regression:** 18/18 PASSED.

---

## 5. Artifact & Dispatch Status
- **Target Notebook:** `205ee2ec-e0d2-4ba6-badf-44f2de02c7e2` (B-SDD Methodology, Multi-Session Handoff & Architecture).
- **Secondary Notebook:** `6813ab1c-ac22-4c3c-9c8e-9dd67e35da99` (B-SDD Legal Cockpit).
- **Source Title:** `INBOX_GEMINI_SPRINT_024_PODROID_LAYA_REPORT`
- **n8n Webhook:** `http://100.66.97.93:5678/webhook/bsdd-supervisor-result`
- **Status:** COMPLETED (SUCCESS)
