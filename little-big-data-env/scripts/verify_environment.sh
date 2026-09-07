#!/usr/bin/env bash

# Big Data Technologies
# Environment Verification Script

echo "=============================================="
echo "    BDT Environment Verification Tool         "
echo "=============================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker could not be found. Please install Docker Desktop or Docker Engine."
    exit 1
else
    echo "✅ Docker is installed."
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ ERROR: Docker Compose (V2) could not be found. Please ensure it is installed."
    exit 1
else
    echo "✅ Docker Compose is available."
fi

# Check Python and Version >= 3.10
if command -v python3 &> /dev/null; then
    PY_CMD="python3"
elif command -v python &> /dev/null; then
    PY_CMD="python"
else
    echo "❌ ERROR: Python is not installed. Please install Python 3.10+ natively on your system."
    exit 1
fi

PY_VER=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PY_CMD -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PY_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "❌ ERROR: Python version must be 3.10 or higher. You have $PY_VER."
    exit 1
else
    echo "✅ Python $PY_VER is installed."
fi

# Get Docker memory limit (rough check)
MEM_LIMIT_BYTES=$(docker info -f '{{.MemTotal}}' 2>/dev/null)
if [ -n "$MEM_LIMIT_BYTES" ]; then
    MEM_LIMIT_GB=$($PY_CMD -c "print(round($MEM_LIMIT_BYTES / 1073741824, 2))")
    echo "✅ Docker Engine Memory: ~$MEM_LIMIT_GB GB"
else
    echo "⚠️  WARNING: Could not determine Docker memory limits."
fi

echo ""
echo "=============================================="
echo "SUCCESS! Local Environment Verification Complete."
echo "Your local system meets the technical requirements."
echo "You may now proceed to launch the Docker containers."
echo "=============================================="
