#!/usr/bin/env bash

cd "$(dirname "$0")"
echo "=== Current working directory ==="
pwd
echo

echo "=== Checking for Python executables ==="
for CMD in py python3 python; do
    if command -v "$CMD" >/dev/null 2>&1; then
        echo "Found $CMD: $(command -v "$CMD")"
        echo
        echo "=== Starting serve_index.py ==="
        "$CMD" serve_index.py
        echo
        echo "=== Server stopped or exited ==="
        read -rp "Press Enter to close this window..."
        exit 0
    fi
done

echo "[ERROR] Python not found."
echo "Please install Python 3 from https://www.python.org/downloads/ or use Homebrew (brew install python)."
echo
read -rp "Press Enter to close this window..."
