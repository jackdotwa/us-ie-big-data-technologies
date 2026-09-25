#!/usr/bin/env python3
"""
Big Data Technologies (BDT)
Cross-Platform Environment Verification Tool
Runs on Windows (PowerShell/CMD/WSL), macOS, and Linux.
"""

import os
import platform
import shutil
import subprocess
import sys


def main():
    print("==============================================")
    print("    BDT Environment Verification Tool         ")
    print("==============================================")
    print()

    # 1. Check Python version >= 3.10
    py_ver_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 10):
        print(f"❌ ERROR: Python version must be 3.10 or higher. Detected: {py_ver_str}.")
        sys.exit(1)
    else:
        print(f"✅ Python {py_ver_str} is installed.")

    # 2. Check Docker binary
    docker_bin = shutil.which("docker")
    if not docker_bin:
        print("❌ ERROR: Docker could not be found. Please install Docker Desktop or Docker Engine.")
        sys.exit(1)
    else:
        print("✅ Docker is installed.")

    # 3. Check Docker Compose (V2 plugin)
    try:
        res = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Docker Compose is available.")
    except Exception:
        print("❌ ERROR: Docker Compose (V2) could not be found. Please ensure Docker Desktop / Compose is installed.")
        sys.exit(1)

    # 4. Check Logical CPU Cores
    cpus = os.cpu_count() or 0
    if 0 < cpus < 4:
        print(f"⚠️  WARNING: Recommended minimum is 4 logical CPU cores. Detected: {cpus} cores.")
    else:
        print(f"✅ Logical CPU Cores: {cpus}")

    # 5. Check System Architecture
    arch = platform.machine()
    print(f"✅ System Architecture: {arch}")

    # 6. Check Docker Engine Memory
    try:
        res = subprocess.run(
            ["docker", "info", "-f", "{{.MemTotal}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        mem_str = res.stdout.strip()
        if mem_str.isdigit():
            mem_bytes = int(mem_str)
            mem_gb = round(mem_bytes / (1024**3), 2)
            if mem_bytes < 6 * (1024**3):
                print(f"⚠️  WARNING: Docker memory allocation is ~{mem_gb} GB. Recommended is 8 GB to avoid container OOM.")
            else:
                print(f"✅ Docker Engine Memory: ~{mem_gb} GB")
        else:
            print("⚠️  WARNING: Could not parse Docker memory limits.")
    except Exception:
        print("⚠️  WARNING: Could not determine Docker memory limits (ensure Docker daemon is running).")

    # 7. Check Available Disk Space in current directory
    try:
        usage = shutil.disk_usage(".")
        free_gb = round(usage.free / (1024**3), 1)
        if free_gb < 10.0:
            print(f"⚠️  WARNING: Available disk space is ~{free_gb} GB. Recommended is 15+ GB for container images.")
        else:
            print(f"✅ Available Disk Space: ~{free_gb} GB")
    except Exception:
        print("⚠️  WARNING: Could not determine available disk space.")

    print()
    print("==============================================")
    print("Local Environment Verification Complete.")
    print("You may now proceed to launch the Docker containers.")
    print("==============================================")


if __name__ == "__main__":
    main()
