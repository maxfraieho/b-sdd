# Laya Decision Engine on Podroid (Google Pixel 7)

## Overview
- **Edge Node:** Google Pixel 7 (Podroid Alpine VM: `192.168.3.251`)
- **Port:** `9623` (REST API)
- **Model:** `laya-multilingual` (mmBERT-base 322M Non-Autoregressive System 1 Decision Engine)
- **Host Offloading Target:** Host .161 (`100.65.225.122` / `192.168.3.161`), protecting Host .161 from OOM kills.

## Architecture
- **Port 9622:** Utopia DB (WORM ledger & bitemporal store)
- **Port 9623:** Laya Decision Engine REST Daemon
- **Sub-40ms Guarantee:** System 1 fast-inference routing for state approval and invariant checks.

## Deployment to Pixel 7 Podroid

1. Copy deploy directory to Pixel 7 Alpine VM:
```bash
scp -r deploy/podroid/* root@192.168.3.251:/opt/laya/
```

2. Inside Podroid Alpine VM:
```bash
cd /opt/laya
./setup_laya_alpine.sh
```

3. Service Management:
- **Using OpenRC (Recommended on Alpine):**
  ```bash
  rc-service podroid-laya start
  rc-service podroid-laya status
  ```
- **Standalone execution:**
  ```bash
  /opt/laya/start_laya.sh
  ```

4. Verify from Host .161:
```bash
curl http://192.168.3.251:9623/health
```
Expected response:
```json
{"status": "ok", "model": "laya-multilingual", "port": 9623, "node": "pixel7-podroid"}
```
