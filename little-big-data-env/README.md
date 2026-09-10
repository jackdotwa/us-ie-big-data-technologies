# Big Data Technologies: Sandbox Environment

Welcome to the local sandbox environment for the Big Data Technologies Master's course. This repository contains a fully containerized, multi-node big data stack designed to run entirely locally on your laptop using Docker.

This environment simulates a real-world industrial data architecture without incurring cloud costs or requiring complex local software installations.

## 1. Prerequisites

Before starting, ensure your system meets the following requirements:
*   **Hardware:** Minimum 8 GB RAM, 4 CPU cores, 10 GB free disk space.
*   **Operating System:** macOS (Intel/Apple Silicon), Windows 10/11 (with WSL2 enabled), or Linux.
*   **Software:**
    *   Docker Desktop (or Docker Engine + Docker Compose v2)
    *   Git
    *   Python 3.11+ (for the host verification script, stream generator, and vector seeding)

## 2. Getting Started & Verification

First, verify that your Docker environment is running and capable of handling the resource limits.

1.  Open your terminal.
2.  Navigate to this directory (`little-big-data-env`).
3.  Run the environment verification script:
    ```bash
    ./scripts/verify_environment.sh
    ```
    *If you are on Windows, run this from within your WSL2 terminal (e.g., Ubuntu).*

## 3. Starting the Analytics Stack

Once verified, you can spin up the entire cluster. We use Docker Compose to orchestrate 6 interconnected containers: Spark Master, Spark Worker, Kafka Broker, Kafka UI, Cassandra, and Qdrant Vector DB.

```bash
docker compose up -d
```

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
docker exec -it spark-master /opt/spark/bin/spark-submit \
    /opt/spark/work-dir/scripts/init_qdrant_data.py
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
docker exec -it kafka du -sh /tmp/kafka-logs
```

## 5. Shutting Down

When you are finished working, it is important to shut down the environment to free up your computer's RAM and CPU.

```bash
docker compose down
```

*(Note: Data in Cassandra and Kafka is ephemeral in this sandbox and will be reset upon container destruction unless volume mounts are explicitly added for their data directories).*
