#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-tests.settings}"

if command -v node >/dev/null 2>&1 && [ -f "$ROOT/package.json" ]; then
  if [ ! -d "$ROOT/node_modules/axe-core" ]; then
    npm ci --prefix "$ROOT" --silent
  fi
fi

if command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  PYTHON=python3
fi

exec "$PYTHON" -m django shard_a11y "$@"
