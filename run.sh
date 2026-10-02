#!/usr/bin/env bash
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then exec python3 payload_builder.py
elif command -v python >/dev/null 2>&1; then exec python payload_builder.py
else echo "Python 3.8+ not found."; exit 1; fi
