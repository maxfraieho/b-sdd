#!/bin/sh
# ==============================================================================
# Setup Laya Decision Engine on Podroid Alpine VM (Google Pixel 7)
# Architecture: aarch64 / Alpine Linux
# Port: 9623
# ==============================================================================
set -e

echo ">>> [1/5] Updating Alpine package repositories..."
apk update

echo ">>> [2/5] Installing base runtime packages (python3, pip, gcompat, curl)..."
apk add --no-cache python3 py3-pip gcompat gcc python3-dev musl-dev linux-headers libffi-dev curl

echo ">>> [3/5] Setting up /opt/laya directory structure..."
mkdir -p /opt/laya/models /var/log/laya /etc/laya

# Copy daemon and scripts into /opt/laya
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "${SCRIPT_DIR}/laya_daemon.py" /opt/laya/laya_daemon.py
chmod +x /opt/laya/laya_daemon.py

if [ -f "${SCRIPT_DIR}/start_laya.sh" ]; then
    cp "${SCRIPT_DIR}/start_laya.sh" /opt/laya/start_laya.sh
    chmod +x /opt/laya/start_laya.sh
fi

echo ">>> [4/5] Installing OpenRC init service if available..."
if [ -d /etc/init.d ] && [ -f "${SCRIPT_DIR}/podroid_laya.initd" ]; then
    cp "${SCRIPT_DIR}/podroid_laya.initd" /etc/init.d/podroid-laya
    chmod +x /etc/init.d/podroid-laya
    rc-update add podroid-laya default || echo "Note: rc-update not in runlevel, service installed manually."
fi

echo ">>> [5/5] Testing Laya daemon binary..."
python3 /opt/laya/laya_daemon.py --help > /dev/null

echo "=============================================================================="
echo "✅ Laya Decision Engine setup complete on Podroid Alpine VM!"
echo "   Start via OpenRC:   rc-service podroid-laya start"
echo "   Start standalone:   /opt/laya/start_laya.sh"
echo "   Test endpoint:      curl http://127.0.0.1:9623/health"
echo "=============================================================================="
