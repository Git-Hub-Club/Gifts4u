#!/usr/bin/env bash
set -euo pipefail

# This project uses the Replit Python runtime directly, so post-merge setup
# only needs to validate the application entrypoints. Keep this non-interactive
# and fast because it runs automatically after every task merge.
python -m py_compile \
  app.py \
  main.py \
  wsgi.py \
  deployment/app.py \
  deployment/main.py \
  deployment/wsgi.py

if ! cmp -s app.py deployment/app.py; then
  echo "deployment/app.py is out of sync with app.py" >&2
  exit 1
fi
