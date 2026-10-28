#!/usr/bin/env bash
# Serves JupyterLab from the lakehouse driver, the stack's edge node, on http://localhost:8888.
# Notebooks open in your repository (/workspace) and their Spark sessions run on the lakehouse
# workers with the fixed configuration in config/lakehouse/spark-defaults.conf.
#   ./little-big-data-env/scripts/start_jupyterlab.sh
# JupyterLab is installed into the driver on first use, and again after the driver is recreated.
# The port is bound to localhost only, so the server runs without a token.
set -euo pipefail

ENV_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$ENV_DIR/docker-compose.yml")
JUPYTERLAB_VERSION="4.2.5"

docker inspect lakehouse-driver >/dev/null 2>&1 \
  || { echo "[!] lakehouse-driver is not running: start it with docker compose --profile lakehouse up -d"; exit 1; }

if "${COMPOSE[@]}" exec -T lakehouse-driver pgrep -f "jupyter-lab" >/dev/null; then
  echo "[=] JupyterLab is already running: http://localhost:8888"; exit 0
fi

if ! "${COMPOSE[@]}" exec -T lakehouse-driver python3 -c "import jupyterlab" 2>/dev/null; then
  echo "[*] Installing JupyterLab $JUPYTERLAB_VERSION in lakehouse-driver"
  "${COMPOSE[@]}" exec -T lakehouse-driver python3 -m pip install -q \
    --default-timeout=120 --retries 5 "jupyterlab==$JUPYTERLAB_VERSION"
fi

echo "[*] Starting JupyterLab"
"${COMPOSE[@]}" exec -d lakehouse-driver sh -c \
  "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
   --ServerApp.token='' --ServerApp.root_dir=/workspace > /tmp/jupyterlab.log 2>&1"

for _ in $(seq 1 30); do
  if curl -fs -o /dev/null http://localhost:8888/api; then
    echo "[+] JupyterLab: http://localhost:8888"
    echo "    In a notebook: from pyspark.sql import SparkSession; spark = SparkSession.builder.getOrCreate()"
    echo "    Run spark.stop() before spark-submit: an open session holds all the cluster's cores."
    exit 0
  fi
  sleep 1
done
echo "[!] JupyterLab did not start; see: docker compose -f $ENV_DIR/docker-compose.yml exec lakehouse-driver cat /tmp/jupyterlab.log"
exit 1
