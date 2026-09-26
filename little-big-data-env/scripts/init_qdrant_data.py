"""
Deterministic Qdrant vector collection initializer.

Populates the `maintenance_logs` collection with synthetic log embeddings
deterministically seeded by an integer seed.
Uses pure Python standard library (urllib.request + json) to interact with Qdrant's
REST API directly, ensuring zero-dependency execution across ARM64, x86_64,
virtual environments, and Docker containers without compiled driver overhead.
"""
import os
import sys
import argparse
import random
import time
import json
import urllib.request
import urllib.error

COLLECTION = "maintenance_logs"
VECTOR_SIZE = 384
N_POINTS = 3

_SYMPTOMS = [
    "spindle motor overheated due to friction",
    "excessive vibration detected on chassis arm",
    "coolant pressure dropped below threshold",
    "tool wear exceeded safe milling tolerance",
    "bearing temperature spike during shuffle load",
    "laser optical sensor calibration drifted",
]
_SEVERITIES = ["LOW", "MEDIUM", "HIGH"]


def generate_qdrant_points(seed, n=N_POINTS):
    """Deterministic payload generator.

    Returns a list of dicts {id, severity, text}.
    """
    rng = random.Random(seed)
    points = []
    for i in range(1, n + 1):
        machine = f"CNC-MILL-{rng.randint(1, 5):02d}"
        symptom = rng.choice(_SYMPTOMS)
        severity = rng.choice(_SEVERITIES)
        text = f"{machine} {symptom}."
        points.append({"id": i, "severity": severity, "text": text})
    return points


def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Qdrant vector database collection initializer."
    )
    parser.add_argument(
        "seed",
        type=int,
        help="Integer seed for deterministic data generation."
    )
    args = parser.parse_args()
    seed = args.seed

    host = os.environ.get("QDRANT_HOST")
    if not host:
        import socket
        try:
            socket.gethostbyname("qdrant")
            host = "qdrant"
        except socket.gaierror:
            host = "localhost"
    port = int(os.environ.get("QDRANT_PORT", "6333"))
    base_url = f"http://{host}:{port}/collections/{COLLECTION}"
    print(f"Connecting to Qdrant at {host}:{port} ...")

    # 1. Wait for Qdrant to accept connections
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(f"http://{host}:{port}/collections")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    break
        except Exception as e:
            if attempt == max_retries:
                print(f"[-] Could not connect to Qdrant after {max_retries} attempts.")
                raise e
            print(f"[*] Waiting for Qdrant to accept connections (attempt {attempt}/{max_retries})...")
            time.sleep(2)

    # 2. Delete collection if exists (idempotency)
    del_req = urllib.request.Request(base_url, method="DELETE")
    try:
        with urllib.request.urlopen(del_req, timeout=5):
            pass
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise

    # 3. Create collection with COSINE distance and VECTOR_SIZE
    create_payload = json.dumps({
        "vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}
    }).encode("utf-8")
    create_req = urllib.request.Request(
        base_url,
        data=create_payload,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(create_req, timeout=5) as resp:
        pass

    # 4. Generate points and upsert
    rng = random.Random(seed)
    meta = generate_qdrant_points(seed)
    struct_points = []
    for p in meta:
        vector = [rng.random() for _ in range(VECTOR_SIZE)]
        struct_points.append({
            "id": p["id"],
            "vector": vector,
            "payload": {"text": p["text"], "severity": p["severity"]}
        })

    upsert_payload = json.dumps({"points": struct_points}).encode("utf-8")
    upsert_req = urllib.request.Request(
        f"{base_url}/points",
        data=upsert_payload,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(upsert_req, timeout=5) as resp:
        pass

    print("======================================================")
    print(f"[+] Successfully seeded points into '{COLLECTION}' with seed {seed}.")
    print(f"Inspect: http://localhost:6333/collections/{COLLECTION}")
    print("======================================================")


if __name__ == "__main__":
    main()
