#!/usr/bin/env bash
set -euo pipefail

echo "=== OS / Kernel ==="
uname -a || true
[ -f /etc/os-release ] && cat /etc/os-release || true

echo
echo "=== Container detection ==="
grep -iE 'docker|kubepods|container' /proc/1/cgroup 2>/dev/null || true
[ -f /run/.containerenv ] && echo "/run/.containerenv present" || true
[ -f /.dockerenv ] && echo "/.dockerenv present" || true
ps -p 1 -o comm= || true

echo
echo "=== CPU / Shell ==="
arch || true
echo "$SHELL" || true

echo
echo "=== Package managers available ==="
for pm in apt-get yum dnf apk pacman brew nix-env choco winget; do
  if command -v "$pm" >/dev/null 2>&1; then
    echo "FOUND: $pm"
  fi
done

echo
echo "=== Common tools ==="
for t in git gh curl jq sudo python3; do
  if command -v "$t" >/dev/null 2>&1; then
    printf "%-8s -> %s\n" "$t" "$($t --version 2>&1 | head -n1)"
  else
    printf "%-8s -> MISSING\n" "$t"
  fi
done

echo
echo "=== Permissions quick-check ==="
if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  echo "sudo: OK (non-interactive)"
else
  echo "sudo: not available or needs password"
fi

echo
echo "=== Network to GitHub API (heads-up: may be blocked) ==="
if command -v curl >/dev/null 2>&1; then
  curl -sS -I https://api.github.com | head -n 1 || true
else
  echo "curl missing"
fi
