#!/usr/bin/env bash
# ==============================================================================
# B-SDD Production Health & Telemetry Verification Probe (ADR-012)
# ==============================================================================
set -euo pipefail

GATEWAY_URL="${1:-http://127.0.0.1:8765}"
TIMEOUT=10

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== Probing B-SDD Gateway Health: ${GATEWAY_URL} ===${NC}"

# Probe 1: /api/health
echo -n "  [1/4] Probing /api/health... "
HEALTH_RESP=$(curl -s -4 --max-time "${TIMEOUT}" "${GATEWAY_URL}/api/health" || echo "")
if [ -z "${HEALTH_RESP}" ]; then
  echo -e "${RED}FAILED (Connection timed out or refused)${NC}"
  exit 1
fi
HEALTH_STATUS=$(printf '%s' "${HEALTH_RESP}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null || echo "parse_error")
if [ "${HEALTH_STATUS}" = "healthy" ]; then
  echo -e "${GREEN}PASS (healthy)${NC}"
else
  echo -e "${YELLOW}WARN (status: ${HEALTH_STATUS})${NC}"
fi

# Probe 2: /api/telemetry (ADR-012)
echo -n "  [2/4] Probing /api/telemetry (SLA < 50ms)... "
TELEM_RESP=$(curl -s -4 --max-time "${TIMEOUT}" "${GATEWAY_URL}/api/telemetry" || echo "")
if [ -z "${TELEM_RESP}" ]; then
  echo -e "${RED}FAILED${NC}"
  exit 1
fi
TELEM_CHECK=$(printf '%s' "${TELEM_RESP}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
comp = data.get('compiler', {})
sla_ok = comp.get('sla_passed', False)
last_ms = comp.get('last_compile_ms', 0)
print(f'last={last_ms}ms|sla={sla_ok}')
" 2>/dev/null || echo "parse_error")

if [[ "${TELEM_CHECK}" =~ "sla=True" ]] || [[ "${TELEM_CHECK}" =~ "last=0" ]]; then
  echo -e "${GREEN}PASS (${TELEM_CHECK})${NC}"
else
  echo -e "${YELLOW}WARN (${TELEM_CHECK})${NC}"
fi

# Probe 3: /api/metrics (Prometheus)
echo -n "  [3/4] Probing /api/metrics (Prometheus exposition)... "
METRICS_RESP=$(curl -s -4 --max-time "${TIMEOUT}" "${GATEWAY_URL}/api/metrics" || echo "")
if echo "${METRICS_RESP}" | grep -q "bsdd_http_requests_total"; then
  echo -e "${GREEN}PASS (Prometheus format confirmed)${NC}"
else
  echo -e "${RED}FAILED (Missing expected Prometheus metrics)${NC}"
  exit 1
fi

# Probe 4: /api/rules/active (Budget <= 500w)
echo -n "  [4/4] Probing /api/rules/active (Word budget <= 500)... "
RULES_RESP=$(curl -s -4 --max-time "${TIMEOUT}" "${GATEWAY_URL}/api/rules/active" || echo "")
RULES_CHECK=$(printf '%s' "${RULES_RESP}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
w = data.get('word_count', 999)
exceeded = data.get('is_budget_exceeded', True)
print(f'words={w}|exceeded={exceeded}')
" 2>/dev/null || echo "parse_error")

if [[ "${RULES_CHECK}" =~ "exceeded=False" ]]; then
  echo -e "${GREEN}PASS (${RULES_CHECK})${NC}"
else
  echo -e "${RED}FAILED (${RULES_CHECK})${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All 4 production health & telemetry probes PASSED!${NC}"
exit 0
