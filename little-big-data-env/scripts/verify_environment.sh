#!/usr/bin/env bash
# Big Data Technologies (BDT)
# Wrapper script for cross-platform Python verification tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 &> /dev/null; then
    exec python3 "${SCRIPT_DIR}/verify_environment.py" "$@"
elif command -v python &> /dev/null; then
    exec python "${SCRIPT_DIR}/verify_environment.py" "$@"
else
    echo "❌ ERROR: Python 3 is not installed or not in your PATH."
    exit 1
fi
