#!/usr/bin/env bash
# ==============================================================================
# B-SDD Podroid Deployment Script (Sprint 025 - Deliverable C)
# Pushes Laya Decision Engine package to Google Pixel 7 (Podroid Alpine VM),
# executes remote setup/start, and verifies HTTP health connectivity.
# ==============================================================================
set -euo pipefail

EDGE_IP="${EDGE_IP:-192.168.3.251}"
EDGE_PORT="${EDGE_PORT:-9623}"
SSH_USER="${SSH_USER:-root}"
SSH_PORT="${SSH_PORT:-22}"
DEPLOY_SRC="${DEPLOY_SRC:-/home/vokov/projects/b-sdd/deploy/podroid}"
REMOTE_DEST="${REMOTE_DEST:-/opt/laya}"

echo "============================================================"
echo "🚀 [B-SDD] Deploying Laya Decision Engine to Pixel 7 Podroid"
echo "   Target Host: ${SSH_USER}@${EDGE_IP}:${EDGE_PORT}"
echo "   Source Directory: ${DEPLOY_SRC}"
echo "   Remote Directory: ${REMOTE_DEST}"
echo "============================================================"

# 1. Connectivity Check (ICMP Ping)
echo -n "📡 Checking ICMP ping to ${EDGE_IP}... "
if ping -c 1 -W 2 "${EDGE_IP}" >/dev/null 2>&1; then
    echo "OK (Host reachable)"
else
    echo "WARN (Host unreachable via ping)"
fi

# 2. Check if SSH is accessible
echo -n "🔑 Testing SSH connection to ${SSH_USER}@${EDGE_IP}:${SSH_PORT}... "
if ssh -o BatchMode=yes -o ConnectTimeout=3 -o StrictHostKeyChecking=no -p "${SSH_PORT}" "${SSH_USER}@${EDGE_IP}" "echo OK" >/dev/null 2>&1; then
    echo "OK (SSH accessible)"
    
    # 3. Create destination directory and push files
    echo "📦 Transferring deployment files to ${EDGE_IP}:${REMOTE_DEST}/..."
    ssh -o StrictHostKeyChecking=no -p "${SSH_PORT}" "${SSH_USER}@${EDGE_IP}" "mkdir -p ${REMOTE_DEST} /root/laya_deploy"
    scp -o StrictHostKeyChecking=no -P "${SSH_PORT}" -r "${DEPLOY_SRC}/"* "${SSH_USER}@${EDGE_IP}:${REMOTE_DEST}/"
    scp -o StrictHostKeyChecking=no -P "${SSH_PORT}" -r "${DEPLOY_SRC}/"* "${SSH_USER}@${EDGE_IP}:/root/"

    # 4. Remote installation and daemon launch
    echo "⚙️ Executing remote setup on Podroid Alpine VM..."
    ssh -o StrictHostKeyChecking=no -p "${SSH_PORT}" "${SSH_USER}@${EDGE_IP}" bash -s << 'EOF'
set -e
cd /opt/laya || cd /root
chmod +x setup_laya_alpine.sh start_laya.sh laya_daemon.py 2>/dev/null || true

# Run setup if python3 or dependencies missing
if ! command -v python3 >/dev/null 2>&1; then
    echo "Installing python3 on Alpine..."
    apk add --no-cache python3 py3-pip
fi

# Stop existing daemon if running
pkill -f laya_daemon.py 2>/dev/null || true
sleep 1

# Start Laya daemon in background
nohup python3 /opt/laya/laya_daemon.py --host 0.0.0.0 --port 9623 > /var/log/laya.log 2>&1 &
sleep 2
echo "Laya daemon launched on Podroid."
EOF

else
    echo "OFFLINE (SSH connection refused or timed out)"
    echo "ℹ️  Note: Pixel 7 Podroid VM may be asleep or power-managed."
    echo "   Ensure Podroid app is active on Pixel 7 with Dropbear/OpenSSH running."
fi

# 5. Verify HTTP Connectivity
echo -n "🏥 Testing Laya REST API health (http://${EDGE_IP}:${EDGE_PORT}/health)... "
HEALTH_RESP=$(curl -s -m 3 "http://${EDGE_IP}:${EDGE_PORT}/health" || true)

if [[ -n "${HEALTH_RESP}" && "${HEALTH_RESP}" == *"status"* ]]; then
    echo "SUCCESS"
    echo "📊 Health Response: ${HEALTH_RESP}"
    exit 0
else
    echo "OFFLINE"
    echo "⚠️  Laya daemon is currently unreachable on http://${EDGE_IP}:${EDGE_PORT}."
    echo "   Host .161 will gracefully fall back to local static heuristics (ADR-002)."
    exit 0
fi
