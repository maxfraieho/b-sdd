# Laya Decision Engine on Podroid (Google Pixel 7)

## Overview
- **Edge Node:** Google Pixel 7 (Podroid Alpine VM: `192.168.3.251`)
- **Port:** `9623` (REST API)
- **Model:** `laya-multilingual` (mmBERT-base 322M Non-Autoregressive System 1 Decision Engine)
- **Host Offloading Target:** Host .161 (`100.65.225.122` / `192.168.3.161`), protecting Host .161 from OOM kills.

## Architecture
- **Port 9622:** Utopia DB (WORM ledger & bitemporal store daemon: `podroid-utopia-worm`)
- **Port 9623:** Laya Decision Engine REST Daemon (`podroid-laya`)
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
  rc-service podroid-utopia-worm start
  rc-service podroid-laya status
  rc-service podroid-utopia-worm status
  ```
- **Port Forwarding via podroid-forward:**
  ```bash
  /usr/local/bin/podroid-forward add 9622 9622 tcp
  /usr/local/bin/podroid-forward add 9623 9623 tcp
  /usr/local/bin/podroid-forward list
  ```
- **Persistent Port Forwarding on Boot:**
  Entries are maintained in `/etc/local.d/port-forwards.start`.

4. Verify from Host .161:
```bash
curl http://192.168.3.251:9623/health
curl http://192.168.3.251:9622/health
```
Expected responses:
```json
{"status": "ok", "model": "laya-multilingual", "port": 9623, "node": "pixel7-podroid"}
{"status": "UP", "service": "utopia_db_worm", "port": 9622, "node": "pixel7-podroid"}
```

