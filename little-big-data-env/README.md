# Big Data Technologies: Sandbox Environment

Welcome to the local sandbox environment for Big Data Technologies. This repository contains a fully containerized, multi-node big data stack designed to run entirely locally on your workstation using Docker.

This environment simulates a real-world industrial data architecture without incurring cloud costs or requiring complex local software installations.

## 1. Prerequisites

Before starting, ensure your system meets the following requirements:
*   **Hardware:** Minimum 8 GB RAM, 4 CPU cores, 10 GB free disk space.
*   **Operating System:** macOS (Intel/Apple Silicon), Windows 10/11 (with WSL2 enabled), or Linux.
*   **Software:**
    *   **Docker:** [Docker Desktop](https://docs.docker.com/get-started/get-docker/) for [Windows](https://docs.docker.com/desktop/setup/install/windows-install/) (with WSL2 backend enabled) and [macOS](https://docs.docker.com/desktop/setup/install/mac-install/) (Apple Silicon / Intel), or [Docker Engine](https://docs.docker.com/engine/install/) with [Compose v2](https://docs.docker.com/compose/install/linux/) for Linux.
    *   **Git:** Follow the installation instructions at [git-scm.com/book/en/v2/Getting-Started-Installing-Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (version 2.30+).
    *   **Python 3.10+:** For host scripts, stream generation, and vector seeding ([python.org](https://www.python.org/downloads/)).

## 2. Getting Started & Verification

First, verify that your Docker environment is running and capable of handling the resource limits.

1.  Open your terminal (PowerShell, Command Prompt, or bash/zsh).
2.  Navigate to this directory (`little-big-data-env`).
3.  Run the cross-platform environment verification tool:
    ```bash
    python scripts/verify_environment.py
    ```
    *(Alternatively, on Linux/macOS you may run `./scripts/verify_environment.sh`)*

## 3. Starting the Analytics Stack

The services are grouped into Docker Compose **profiles**, and nothing starts without one. The course's lab stack (Spark Master, Spark Worker, Kafka Broker, Kafka UI, Cassandra, and Qdrant Vector DB) is the `analytics` profile:

```bash
docker compose --profile analytics up -d
```

| Profile | Starts |
| --- | --- |
| `analytics` | Spark master and worker, Kafka, Kafka UI, the stream consumer, Cassandra, Qdrant |
| `streaming` | Spark master and worker, Kafka, Kafka UI, the stream consumer |
| `spark` | Spark master and worker |
| `lakehouse` | S3 object store, Spark master with two larger workers and a driver, Iceberg (Section 6) |

A service shared by several profiles (such as `spark-master`) runs once, whichever of its profiles you start. Naming a service starts it whatever its profile, for example `docker compose up -d cassandra`. Start only what your work needs: every container takes memory.

You can verify the containers are running with:
```bash
docker ps
```

## 4. Interacting with the Environment

### A. Web Interfaces (Observability)
Once the stack is running, you can monitor the systems via your web browser:
*   **Spark Master UI:** [http://localhost:8080](http://localhost:8080) (Cluster overview)
*   **Spark Job UI:** [http://localhost:4040](http://localhost:4040) (Available only when a Spark job is running)
*   **Kafka UI:** [http://localhost:8081](http://localhost:8081) (Topic and consumer monitoring)
*   **Qdrant REST API:** [http://localhost:6333/collections](http://localhost:6333/collections) (Vector DB status)

### B. Executing Code (Zero Local Install)
To avoid dependency issues, all data engineering code is executed *inside* the containers. We have volume-mounted the `jobs/`, `scripts/`, and `config/` directories into the Spark containers. This means you can edit code on your host machine using VSCode, and run it inside the container.

**Run the Baseline Spark Job:**
```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    /opt/spark/work-dir/jobs/run_spark_baseline.py
```

**Run the Advanced Telemetry ETL Script:**
```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work-dir/jobs/advanced_telemetry_etl.py
```

**Generate Synthetic Factory Telemetry Data (Kafka):**
```bash
docker exec -it spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work-dir/jobs/generate_stream.py
```

**Initialize Qdrant Vector Database:**
```bash
python scripts/init_qdrant_data.py <SEED>
```

### C. Accessing Databases

**Cassandra CQL Shell:**
You can interact with the NoSQL database directly using its query language.
```bash
docker exec -it cassandra cqlsh
```

**Measuring Kafka Storage Consumption:**
You can inspect the physical disk footprint of the Kafka topics on the broker.
```bash
docker exec kafka du -sk /tmp/kafka-logs
```

## 5. Shutting Down

When you are finished working, it is important to shut down the environment to free up your computer's RAM and CPU.

```bash
docker compose --profile <profile> down
```

*(Note: Data in Cassandra and Kafka is ephemeral in this sandbox and will be reset upon container destruction unless volume mounts are explicitly added for their data directories).*

## 6. Lakehouse Stack (S3, Spark, Iceberg)

The `lakehouse` profile is an S3 object store with Spark and Iceberg on top. Its memory limits add up to 8 GiB, so start it on its own, not alongside `analytics`. Run everything from the repository root.

| Service | Purpose | Memory limit |
| --- | --- | --- |
| `seaweedfs` | S3-compatible object store (SeaweedFS), buckets `landing`, `warehouse`, `output`, `logs` | 1 GiB |
| `spark-master` | Spark standalone master (shared with the other profiles), UI on http://localhost:8080 | 512 MiB |
| `lakehouse-worker-1`, `lakehouse-worker-2` | 2 cores and 2 GiB each: one executor per worker | 2.5 GiB each |
| `lakehouse-driver` | Where you run `spark-submit`, with your repository (`REPO_DIR`) mounted at `/workspace`; application UI on http://localhost:4041 | 1.25 GiB |

**Where Iceberg sits.** Iceberg is not a service: it is a table format, used through a library inside Spark. The Iceberg Spark runtime jar gives Spark SQL a catalog called `lake`, whose tables live as Parquet data files plus Iceberg metadata (snapshots and manifests) in the `warehouse` bucket. Raw files stay in `landing`; your jobs turn them into tables in `lake`; results go to `output`.

1. Download the Iceberg and S3A jars once (about 320 MB, checked against Maven Central):
   ```bash
   ./little-big-data-env/scripts/fetch_iceberg_s3a_jars.sh
   ```
2. Start the stack, with your own repository mounted in the driver:
   ```bash
   REPO_DIR=/path/to/your/repository docker compose -f little-big-data-env/docker-compose.yml --profile lakehouse up -d
   ```
3. Load a retail data tarball into the `landing` bucket:
   ```bash
   ./little-big-data-env/scripts/load_retail_to_landing.sh /path/to/<tarball>.tar.gz
   ```
4. Check the stack end to end (reads landing, writes Iceberg and Parquet, leaves an event log):
   ```bash
   docker compose -f little-big-data-env/docker-compose.yml exec lakehouse-driver spark-submit little-big-data-env/jobs/lakehouse_smoke.py
   ```

**Fixed configuration.** `config/lakehouse/spark-defaults.conf` sets memory, cores, the S3 endpoint, event logging to `s3a://logs/spark-events/` and the Iceberg catalog `lake` (warehouse `s3a://warehouse/iceberg`). Do not override any of it in your code: every run's event log records the configuration it ran with. Iceberg's vectorised reader is switched off because it crashes the JVM on ARM machines.

**S3 credentials** (inside the stack): endpoint `http://seaweedfs:8333`, access key `bdtadmin`, secret `bdtadmin`. From your host the endpoint is `http://localhost:8333`.

**If you recreate the master** (for example after changing the compose file), restart the workers so they register again:
```bash
docker compose -f little-big-data-env/docker-compose.yml restart lakehouse-worker-1 lakehouse-worker-2
```

**Shut down** with `docker compose -f little-big-data-env/docker-compose.yml --profile lakehouse down`. Add `-v` to delete the object store's volume and all data in it.
