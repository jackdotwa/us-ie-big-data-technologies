# Big Data Technologies: Sandbox Environment

Welcome to the local sandbox environment for Big Data Technologies. This repository contains a fully containerized, multi-node big data stack designed to run entirely locally on your workstation using Docker.

This environment simulates a real-world industrial data architecture without incurring cloud costs or requiring complex local software installations.

## 1. Prerequisites

Before starting, ensure your system meets the following requirements:
*   **Hardware:** Minimum 8 GB RAM (16 GB recommended), 4 CPU cores, 10 GB free disk space. The lakehouse profile (Section 6) needs 10 GB of memory allocated to Docker.
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

The `lakehouse` profile is an S3 object store with Spark and Iceberg on top. Its memory limits add up to 8 GiB, so start it on its own, not alongside `analytics`. Docker Desktop must be allowed at least 10 GB of memory, or the containers cannot use the memory they are allowed: on macOS under Settings → Resources; on Windows with the WSL 2 backend through `memory=10GB` in `%UserProfile%\.wslconfig` (then `wsl --shutdown`). On Linux, Docker uses the machine's memory directly: there is nothing to set, but about 10 GB must be free. Run these commands from the repository root (the folder that contains `little-big-data-env/`), not from inside `little-big-data-env/` as in Section 2.

| Service | Purpose | Memory limit |
| --- | --- | --- |
| `seaweedfs` | S3-compatible object store (SeaweedFS), buckets `landing`, `warehouse`, `output`, `logs` | 1 GiB |
| `spark-master` | Spark standalone master (shared with the other profiles), UI on http://localhost:8080 | 512 MiB |
| `lakehouse-worker-1`, `lakehouse-worker-2` | 2 cores and 2 GiB each: one executor per worker | 2.5 GiB each |
| `lakehouse-driver` | Where you run `spark-submit`, with your repository (`REPO_DIR`) mounted at `/workspace`; application UI on http://localhost:4041; JupyterLab on http://localhost:8888 when started | 1.5 GiB |

**Where Iceberg sits.** Iceberg is not a service: it is a table format, used through a library inside Spark. The Iceberg Spark runtime jar gives Spark SQL a catalog called `lake`, whose tables live as Parquet data files plus Iceberg metadata (snapshots and manifests) in the `warehouse` bucket. Raw files stay in `landing`; your jobs turn them into tables in `lake`; results go to `output`.

1. Download the Iceberg and S3A jars once (about 320 MB, checked against Maven Central):
   ```bash
   ./little-big-data-env/scripts/fetch_iceberg_s3a_jars.sh
   ```
2. Start the stack, with your own repository mounted in the driver. `REPO_DIR` is the absolute path of your local clone of your own course repository; the driver mounts it at `/workspace`, so a path such as `pb2/run_week.py` is resolved inside it:
   ```bash
   REPO_DIR=/path/to/your/repository \
     docker compose -f little-big-data-env/docker-compose.yml --profile lakehouse up -d
   ```
   The driver runs as root. On Linux (including WSL 2), files it creates in your repository, such as notebooks, `__pycache__` folders or anything your code writes there, therefore belong to root. If you cannot edit or delete one, take them back (no `sudo` needed; run it from the repository root while the stack is up):
   ```bash
   docker compose -f little-big-data-env/docker-compose.yml exec lakehouse-driver chown -R "$(id -u):$(id -g)" /workspace
   ```
   macOS is not affected.
3. Load a retail data tarball into the `landing` bucket:
   ```bash
   ./little-big-data-env/scripts/load_retail_to_landing.sh /path/to/<tarball>.tar.gz
   ```
4. Check the stack end to end, in about 3 minutes (reads landing, writes an Iceberg table and Parquet, reads them back and deletes them again, and leaves an event log):
   ```bash
   docker compose -f little-big-data-env/docker-compose.yml exec lakehouse-driver spark-submit /opt/lakehouse/jobs/lakehouse_smoke.py
   ```

**Notebooks (JupyterLab on the edge node).** The driver can also serve JupyterLab, the way a notebook server sits on the edge node of a shared cluster:
```bash
./little-big-data-env/scripts/start_jupyterlab.sh
```
It installs JupyterLab in `lakehouse-driver` on first use (and again after the driver is recreated) and serves it on http://localhost:8888, opened in your repository. In a notebook, `SparkSession.builder.getOrCreate()` runs on the same workers, buckets and fixed configuration as `spark-submit`. VS Code can connect to the same server as a remote Jupyter kernel. The image provides PySpark and no other Python libraries (no pandas, for example): install what you choose to use with `docker compose -f little-big-data-env/docker-compose.yml exec lakehouse-driver python3 -m pip install <package>`. Packages installed this way are lost when the driver is recreated, and anything your own code imports belongs, pinned, in your repository's requirements file. A notebook's Spark session is an application of its own and holds all the cluster's cores while it is open (see http://localhost:8080): call `spark.stop()`, or shut down the kernel, before you run `spark-submit`, which otherwise waits with "Initial job has not accepted any resources".

**Fixed configuration.** `config/lakehouse/spark-defaults.conf` sets memory, cores, the S3 endpoint, event logging to `s3a://logs/spark-events/` and the Iceberg catalog `lake` (warehouse `s3a://warehouse/iceberg`). Do not override any of it in your code: every run's event log records the configuration it ran with. Iceberg's vectorised reader is switched off because it crashes the JVM on ARM machines. `config/lakehouse/log4j2.properties` sets the driver's logging to WARN and hides four harmless warnings this stack prints on every run; it changes nothing about how a job runs. For more detail while debugging, call `spark.sparkContext.setLogLevel("INFO")` in your code; the log level is not part of the fixed configuration.

**S3 credentials** (inside the stack): endpoint `http://seaweedfs:8333`, access key `bdtadmin`, secret `bdtadmin`. From your host the endpoint is `http://localhost:8333`.

**If you recreate the master** (for example after changing the compose file), restart the workers so they register again:
```bash
docker compose -f little-big-data-env/docker-compose.yml restart lakehouse-worker-1 lakehouse-worker-2
```

**Shut down** with `docker compose -f little-big-data-env/docker-compose.yml --profile lakehouse down`. Add `-v` to delete the object store's volume and all data in it.
