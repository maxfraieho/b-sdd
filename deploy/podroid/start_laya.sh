#!/bin/sh
# Start Laya Daemon in background with process tracking
mkdir -p /var/log/laya
PIDFILE="/run/podroid-laya.pid"

if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Laya daemon already running with PID $PID"
        exit 0
    fi
fi

nohup /usr/bin/python3 /opt/laya/laya_daemon.py --host 0.0.0.0 --port 9623 > /var/log/laya/laya.log 2>&1 &
PID=$!
echo $PID > "$PIDFILE"
echo "Laya daemon started with PID $PID. Logs: /var/log/laya/laya.log"
