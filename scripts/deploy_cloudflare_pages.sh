#!/usr/bin/env bash
# ==============================================================================
# B-SDD Cloudflare Pages Automated Deployer
# Deploys b-sdd-ui/dist to Cloudflare Pages via sovereign host 192.168.3.184
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REMOTE_HOST="192.168.3.184"
CF_ACCOUNT_ID="${CF_ACCOUNT_ID:-c354ea45a11a1e1c14f1f41fe780cb34}"
PROJECT_NAME="b-sdd-ui"

echo "=== [1/4] Pre-flight compilation & tests ==="
cd "${ROOT_DIR}"
python3 -m src.cli.main compile
/home/vokov/.local/bin/pytest -q tests/test_drakon_skill_editing.py tests/test_skill_taxonomy_and_protection.py tests/test_workbench_server.py


echo "=== [2/4] Building production frontend bundle ==="
cd "${ROOT_DIR}/b-sdd-ui"
npm run build

echo "=== [3/4] Synchronizing dist/ to sovereign runner (${REMOTE_HOST}) ==="
rsync -avz "${ROOT_DIR}/b-sdd-ui/dist/" "${REMOTE_HOST}:${ROOT_DIR}/b-sdd-ui/dist/"

echo "=== [4/4] Deploying to Cloudflare Pages ==="
ssh "${REMOTE_HOST}" "
  CF_ENV_FILE='/home/vokov/workspace/ai-drakon-scaffolder/cloudflare-worker/.env'
  if [ -f \"\${CF_ENV_FILE}\" ]; then
    TOKEN=\$(grep '^CLOUDFLARE_API_TOKEN=' \"\${CF_ENV_FILE}\" | cut -d '=' -f 2)
  else
    TOKEN=\"\${CLOUDFLARE_API_TOKEN:-}\"
  fi
  if [ -z \"\${TOKEN}\" ]; then
    echo '❌ Error: CLOUDFLARE_API_TOKEN not found'
    exit 1
  fi
  CLOUDFLARE_ACCOUNT_ID='${CF_ACCOUNT_ID}' CLOUDFLARE_API_TOKEN=\"\${TOKEN}\" npx wrangler pages deploy /home/vokov/projects/b-sdd/b-sdd-ui/dist --project-name='${PROJECT_NAME}' --branch=main
"

echo ""
echo "✓ B-SDD Operator Workbench deployed successfully!"
echo "  - Live UI     : https://${PROJECT_NAME}.pages.dev"
echo "  - Live Gateway: https://bsdd.exodus.pp.ua/api/health"
