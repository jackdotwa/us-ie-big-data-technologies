"""
Deterministic Cassandra sensor readings table initializer.

Loads the `factory_telemetry.sensor_readings` table with 100 telemetry rows
deterministically generated based on an integer seed.
"""
import os
import sys
import argparse
import subprocess
import random
import time


def _import_driver():
    import tempfile
    site_packages = os.path.join(tempfile.gettempdir(), "bdt-site-packages")
    try:
        sys.path.insert(0, site_packages)
        from cassandra.cluster import Cluster
    except ImportError:
        print(f"cassandra-driver not found. Installing to {site_packages}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "cassandra-driver", "--target", site_packages])
        import importlib
        importlib.invalidate_caches()
        from cassandra.cluster import Cluster
    return Cluster

KEYSPACE = "factory_telemetry"
TABLE = "sensor_readings"
N_ROWS = 100


def generate_cassandra_rows(seed, n=N_ROWS):
    """Deterministic telemetry row generator.

    Produces sensor readings with deterministic machine_id, product_id,
    spindle_temperature_c, and status values based on seed.
    """
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        machine_id = f"CNC-MILL-{rng.randint(1, 5):02d}"
        variant = rng.choice(["L", "M", "H"])
        product_id = f"{variant}{rng.randint(10000, 99999)}"
        # Simulate standard operations with ~5% over-temperature safety breaches (> 85 C)
        if rng.random() < 0.05:
            temp = round(rng.uniform(86.0, 94.0), 2)
        else:
            temp = round(rng.gauss(65.0, 6.0), 2)
        rows.append({
            "machine_id": machine_id,
            "product_id": product_id,
            "spindle_temperature_c": temp,
            "status": "ACTIVE",
        })
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Cassandra sensor readings table initializer."
    )
    parser.add_argument(
        "seed",
        type=int,
        help="Integer seed for deterministic data generation."
    )
    args = parser.parse_args()
    seed = args.seed

    Cluster = _import_driver()
    host = os.environ.get("CASSANDRA_HOST")
    if not host:
        import socket
        try:
            socket.gethostbyname("cassandra")
            host = "cassandra"
        except socket.gaierror:
            host = "localhost"
    print(f"Connecting to Cassandra at {host}:9042 ...")
    cluster = Cluster([host], port=9042)
    session = None
    max_retries = 20
    for attempt in range(1, max_retries + 1):
        try:
            session = cluster.connect()
            break
        except Exception as e:
            if attempt == max_retries:
                print(f"[-] Could not connect to Cassandra after {max_retries} attempts.")
                raise e
            print(f"[*] Waiting for Cassandra to accept connections (attempt {attempt}/{max_retries})...")
            time.sleep(3)

    session.execute(
        f"CREATE KEYSPACE IF NOT EXISTS {KEYSPACE} "
        "WITH REPLICATION = {'class':'SimpleStrategy','replication_factor':1};"
    )
    session.set_keyspace(KEYSPACE)
    session.execute(
        f"CREATE TABLE IF NOT EXISTS {TABLE} ("
        "machine_id text, event_id uuid, timestamp timestamp, product_id text, "
        "spindle_temperature_c double, status text, "
        "PRIMARY KEY (machine_id, event_id));"
    )
    # Idempotent: clear any previous seeding so re-runs are clean.
    session.execute(f"TRUNCATE {TABLE};")

    import uuid
    from datetime import datetime, timedelta
    insert = session.prepare(
        f"INSERT INTO {TABLE} (machine_id, event_id, timestamp, product_id, "
        "spindle_temperature_c, status) VALUES (?, ?, ?, ?, ?, ?)"
    )
    base = datetime(2026, 8, 22, 4, 54, 29)
    rows = generate_cassandra_rows(seed)
    for i, r in enumerate(rows):
        session.execute(insert, (
            r["machine_id"], uuid.uuid4(), base - timedelta(seconds=i),
            r["product_id"], r["spindle_temperature_c"], r["status"],
        ))

    print(f"[+] Seeded {len(rows)} rows into {KEYSPACE}.{TABLE} with seed {seed}.")
    cluster.shutdown()


if __name__ == "__main__":
    main()
