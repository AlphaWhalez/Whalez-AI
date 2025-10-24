#!/usr/bin/env bash
set -euo pipefail

say() { printf "\n\033[1;36m▶ %s\033[0m\n" "$*"; }

ROOT="$(pwd)"

# 0) Sanity checks
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1"; exit 1; }; }
need git; need python3; need pip3; need npm

# 1) Python env + deps
say "Create/refresh Python venv + requirements"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip wheel setuptools

if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
else
  # base deps fallback (safe no-ops if already installed in your repo)
  pip install psutil requests
fi

# 2) PM2 setup
say "Install/refresh PM2"
npm install -g pm2@latest

say "Clear any existing PM2 processes"
pm2 delete all || true

say "Start Whalez services under PM2"
# Adjust paths if your tree differs; these match your screenshots
pm2 start src/agents/proxy/whalez_us_proxy.py   --name "Whalez-US-Proxy" --interpreter python3
pm2 start src/admin/console_server.py           --name "AdminConsole"   --interpreter python3
pm2 start src/security/sentinel.py              --name "Sentinel"       --interpreter python3
pm2 save

say "PM2 status"
pm2 ls || true

# 3) Health monitor (prove ports) — run briefly so the script can continue
if [[ -f scripts/start_health_monitor.sh ]]; then
  say "Run health monitor for ~15s to verify ports"
  timeout 15 bash scripts/start_health_monitor.sh || true
else
  say "Health monitor script not found, skipping"
fi

# 4) Ensure repo structure and placeholders
say "Ensure data/.gitkeep exists (avoid committing runtime JSON)"
mkdir -p data
[ -f data/.gitkeep ] || touch data/.gitkeep

# 5) Git housekeeping: ignore runtime + build outputs
say "Harden .gitignore for Codex/GitHub PRs"
IGNORES=$'# Ignore runtime & build outputs\n\
data/\n\
node_modules/\n\
android/\n\
ios/\n\
web/assets/\n\
*.log\n\
*.zip\n\
*.jsonl\n\
*.xcarchive\n\
cap/build/\n'
# Add if not already present
grep -q "Ignore runtime & build outputs" .gitignore 2>/dev/null || printf '%s\n' "$IGNORES" >> .gitignore

# 6) Untrack anything already cached that violates the above
say "Untrack cached binaries/build artifacts (safe if none)"
git rm -r --cached --ignore-unmatch data/ node_modules/ android/ ios/ web/assets/ || true
git rm -r --cached --ignore-unmatch **/*.zip **/*.log **/*.jsonl **/*.xcarchive 2>/dev/null || true

# 7) Rebuild Git index cleanly (fixes Codex 400/FRA)
say "Rebuild Git index and prune stale objects"
rm -f .git/index
git reset
git add -A

# 8) Commit
say "Create clean commit for PR"
git commit -m "Deploy Whalez-AI enterprise stack: PM2 services, health monitor, and repo hygiene" || true

# 9) (Optional) Deep clean of Git object store (helps when Codex saw binaries before)
say "Run Git GC + repack (optional but recommended)"
git gc --prune=now
git repack -adf || true

say "All set. In Codex, press: Push → Create PR"
