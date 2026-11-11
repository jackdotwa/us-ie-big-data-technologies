# Streaming starter

A local stack for streaming jobs: Apache Beam (Python 3.10) on Flink 1.19, with Postgres and SeaweedFS (S3), a single-node Kafka for local testing, and an optional lab with JupyterLab, DuckDB and Spark batch. It runs on x86-64 and on Apple silicon / arm64.

## What you need

- Docker Desktop or Docker Engine with **8 GiB of memory** for Docker.
- About **25 GB of free disk**. From an empty Docker to a running job takes about 21 GB: about 10 GB of images, a build cache of about 7 GB (on Docker's containerd image store it can't be pruned while the image exists), and about 2 GB of copies of the Kafka jar. The lab image adds about 2 GB.
- Pull and build before you need it. The downloads are large, and Docker Hub rate-limits busy networks.

## Start

```bash
docker compose --profile stream --profile localkafka build   # your job's image (images/beam + your requirements)
docker compose --profile stream --profile localkafka up -d   # Flink, job server, Postgres, SeaweedFS, Kafka
docker compose run --rm topics                               # create the topics on the local Kafka
docker compose run --rm submit                               # submit pipeline.py to Flink
docker compose stop expansion                                # once the job is RUNNING: frees 0.6 to 1.4 GiB
```

- Flink UI: http://localhost:8081. The first start downloads the Kafka jar (840 MB) into a volume, so the first submit can take a few minutes.
- `pipeline.py` is a stack check, not a real job. It reads two topics, counts records per minute, and writes each count to Postgres (table `stackcheck`) and SeaweedFS (`s3://raw/stackcheck/`). If `docker compose logs taskmanager | grep STACKCHECK` shows lines, the stack works end to end. Records must arrive on the topics for counts to appear.
- The lab: `docker compose --profile lab build`, then `docker compose --profile lab up -d`, and open http://localhost:8888 (token `lab`). It sees the same Postgres and S3 store.
- All ports listen on localhost only.

## Settings

Nothing needs setting for local use. To change the defaults, copy `.env.example` to `.env`:

- `CONNECTION`: the connection file, which holds the Kafka address, login and topic names. The default is `connection/local.env`, for the local Kafka. For another Kafka, save its connection file in `connection/` (see `connection/remote.env.example` for its shape) and set `CONNECTION` to it. Then run `docker compose --profile stream up -d` again, so the TaskManager picks it up. Connection files other than `local.env` are git-ignored.
- `PIPELINE_DIR`: the folder that holds your job, as `pipeline.py` and `requirements.txt`. The default is this folder, so the simplest layout is to copy this folder's contents into your job's folder and run every command from there.
- `LAB_DIR`: the folder the lab opens.

Your job should read every topic name and connection setting from the environment, as `pipeline.py` does. Then the same code runs against any Kafka by changing only the connection file.

## Your code

- **Python libraries:** add them to `requirements.txt`, then `docker compose --profile stream build` and `docker compose --profile stream up -d`. Your code runs inside the `taskmanager` container.
- **Options** for Flink and for your job, such as `--checkpointing_interval` or `--code_version`, must be declared in a `PipelineOptions` subclass, as `StackOptions` does in `pipeline.py`. Otherwise the Python SDK drops them as "unparseable". Extra arguments to `submit` are passed on, for example `docker compose run --rm submit --code_version=$(git describe --tags --always)`.
- **Logs:** `docker compose logs -f taskmanager` shows your Python logging, and tracebacks if the worker fails to start.
- **One file, or installed packages.** The Python worker runs inside the `taskmanager` container and gets your job by pickling it, not by reading your folder. Keep your code in `pipeline.py`, and import third-party libraries inside `setup()` or `process()`, as `pipeline.py` does. A helper module next to `pipeline.py` won't be importable on the worker.
- **Parallelism.** `docker-compose.yml` sets `parallelism.default: 1` and the TaskManager has 2 slots. To run with more, pass it to the runner: `docker compose run --rm submit --parallelism=2`. A source can't use more parallel readers than its topic has partitions.
- **Writing objects.** Writing to the S3 store with a key that already exists overwrites the earlier object.
- **Timing.** A topic can be replayed faster than real time, so measure how long your job takes by Kafka broker timestamps: the time an input record was written against the time your output record was written. Event fields and your own wall clock don't measure it.

## Stop, restart and resume

- **Stop a job:** press Cancel in the Flink UI, or run `curl -X PATCH "localhost:8081/jobs/<job id>?mode=cancel"`. Cancel the old job before you submit a new one, because each submit starts a new job.
- **Crashes recover by themselves.** If your Python code crashes or runs out of memory, or the TaskManager restarts, Flink restarts the job from the last checkpoint (every 30 s) within about a minute. Records after that checkpoint are processed again.
- **A new submit does not resume.** It starts from `auto.offset.reset`, which is `earliest` in `pipeline.py`, so it replays the topic. To carry on where a cancelled job stopped, pass its last checkpoint:
  ```bash
  docker compose exec jobmanager ls /checkpoints/<old job id>        # e.g. chk-14
  docker compose run --rm submit --savepoint_path=/checkpoints/<old job id>/chk-14
  ```
- Keep a stable consumer group (`CONSUMER_GROUP` in the connection file). Don't use `commit_offset_in_finalize=True` with `ReadFromKafka`: on Flink, the job looks RUNNING but restarts every few seconds.

## When something goes wrong

| Symptom | Fix |
|---|---|
| A submit fails with `UNAVAILABLE`, or the expansion service is "OOMKilled" | `docker compose up -d expansion`, wait about 20 s, and submit again. |
| A submit hangs, or the job won't start after many submit/cancel cycles | `docker compose restart taskmanager`, then submit again. |
| "No space left on device" | `docker system df` shows what uses space. Remove images you no longer need with `docker image rm`. On the containerd image store, `docker builder prune` frees little, because the build cache is shared with the images. |
| "port is already allocated" | Another program uses that port (8081, 8333, 5432, 9092 or 8888). Stop it, or change the left-hand port in `docker-compose.yml`. |
| The job is RUNNING but you see no `STACKCHECK` lines | Check that records are arriving on your topics, and read `docker compose logs taskmanager` for Python errors. |
| Docker Hub `429 Too Many Requests` | Wait and retry, or pull from another network. |

## Memory (measured on arm64 and x86-64)

| | In use |
|---|---|
| Stream profile and local Kafka, job running | about 2.3 GiB (TaskManager with Python 0.9, JobManager 0.55, job server 0.55, Kafka 0.25, Postgres and SeaweedFS 0.1) |
| While submitting | 0.6 to 1.4 GiB more, for the expansion service (stop it afterwards) |
| Lab | about 0.1 GiB idle, about 0.5 GiB running a local Spark job |
| Everything (stream, local Kafka and lab), job running | about 3 GiB, up to about 4.5 GiB while submitting |
