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

# Check Python and Version >= 3.11
if command -v python3 &> /dev/null; then
    PY_CMD="python3"
elif command -v python &> /dev/null; then
    PY_CMD="python"
else
    echo "❌ ERROR: Python is not installed. Please install Python 3.11+ natively on your system."
    exit 1
fi

PY_VER=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$($PY_CMD -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PY_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]); then
    echo "❌ ERROR: Python version must be 3.11 or higher. You have $PY_VER."
    exit 1
else
    echo "✅ Python $PY_VER is installed."
fi

# Check Logical CPU Cores
N_CPUS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 0)
if [ "$N_CPUS" -gt 0 ] && [ "$N_CPUS" -lt 4 ]; then
    echo "⚠️  WARNING: Recommended minimum is 4 logical CPU cores. Detected: $N_CPUS cores."
elif [ "$N_CPUS" -ge 4 ]; then
    echo "✅ Logical CPU Cores: $N_CPUS"
fi

# Check Architecture
ARCH=$(uname -m)
echo "✅ System Architecture: $ARCH"

# Get Docker memory limit
MEM_LIMIT_BYTES=$(docker info -f '{{.MemTotal}}' 2>/dev/null)
if [ -n "$MEM_LIMIT_BYTES" ]; then
    MEM_LIMIT_GB=$($PY_CMD -c "print(round($MEM_LIMIT_BYTES / 1073741824, 2))")
    if [ "$($PY_CMD -c "print(1 if $MEM_LIMIT_BYTES < 6442450944 else 0)")" -eq 1 ]; then
        echo "⚠️  WARNING: Docker memory is ~$MEM_LIMIT_GB GB. Recommended is 8 GB to avoid container OOM."
    else
        echo "✅ Docker Engine Memory: ~$MEM_LIMIT_GB GB"
    fi
else
    echo "⚠️  WARNING: Could not determine Docker memory limits."
fi

# Check available disk space in current directory
FREE_DISK_KB=$(df -k . 2>/dev/null | awk 'NR==2 {print $4}')
if [ -n "$FREE_DISK_KB" ]; then
    FREE_DISK_GB=$($PY_CMD -c "print(round($FREE_DISK_KB / 1048576, 1))")
    if [ "$FREE_DISK_KB" -lt 10485760 ]; then
        echo "⚠️  WARNING: Available disk space is ~$FREE_DISK_GB GB. Recommended is 15+ GB for container images."
    else
        echo "✅ Available Disk Space: ~$FREE_DISK_GB GB"
    fi
fi

echo ""
echo "=============================================="
echo "Local Environment Verification Complete."
echo "You may now proceed to launch the Docker containers."
echo "=============================================="
