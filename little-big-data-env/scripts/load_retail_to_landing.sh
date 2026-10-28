#!/usr/bin/env bash
# Loads a retail data tarball into the landing bucket of the running lakehouse stack
# (docker compose --profile lakehouse up -d).
#   ./little-big-data-env/scripts/load_retail_to_landing.sh <tarball>.tar.gz
# Checks the tarball against <tarball>.sha256 when that file is present, extracts it to a
# temporary folder, copies landing/ into s3://landing/, then deletes the temporary folder.
set -euo pipefail

TARBALL="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
ENV_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$ENV_DIR/.retail-load"
# The compose network the object store is on (named after the project folder).
NETWORK="$(docker inspect seaweedfs -f '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null)" \
  || { echo "[!] seaweedfs is not running: start it with docker compose --profile lakehouse up -d"; exit 1; }

if [ -f "$TARBALL.sha256" ]; then
  echo "[*] Checking SHA-256"
  (cd "$(dirname "$TARBALL")" && sha256sum -c "$(basename "$TARBALL").sha256")
fi

rm -rf "$TMP" && mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT
echo "[*] Extracting"
tar -xzf "$TARBALL" -C "$TMP"
test -d "$TMP/landing" || { echo "[!] No landing/ folder in $TARBALL"; exit 1; }

echo "[*] Copying into s3://landing/"
docker run --rm --network "$NETWORK" -v "$TMP/landing:/src:ro" \
  -e RCLONE_CONFIG_S3_TYPE=s3 -e RCLONE_CONFIG_S3_PROVIDER=SeaweedFS \
  -e RCLONE_CONFIG_S3_ENDPOINT=http://seaweedfs:8333 \
  -e RCLONE_CONFIG_S3_ACCESS_KEY_ID=bdtadmin -e RCLONE_CONFIG_S3_SECRET_ACCESS_KEY=bdtadmin \
  rclone/rclone:1.75.2 copy /src s3:landing --transfers 32 --checkers 32 --stats-one-line --stats 30s
docker run --rm --network "$NETWORK" \
  -e RCLONE_CONFIG_S3_TYPE=s3 -e RCLONE_CONFIG_S3_PROVIDER=SeaweedFS \
  -e RCLONE_CONFIG_S3_ENDPOINT=http://seaweedfs:8333 \
  -e RCLONE_CONFIG_S3_ACCESS_KEY_ID=bdtadmin -e RCLONE_CONFIG_S3_SECRET_ACCESS_KEY=bdtadmin \
  rclone/rclone:1.75.2 size s3:landing
echo "[+] Loaded"
