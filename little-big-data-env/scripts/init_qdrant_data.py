"""
Deterministic Qdrant vector collection initializer.

Populates the `maintenance_logs` collection with synthetic log embeddings
deterministically seeded by an integer seed.
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
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PointStruct
    except ImportError:
        print(f"qdrant-client not found. Installing to {site_packages}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "qdrant-client", "--target", site_packages])
        import importlib
        importlib.invalidate_caches()
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PointStruct
    return QdrantClient, Distance, VectorParams, PointStruct

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

    QdrantClient, Distance, VectorParams, PointStruct = _import_driver()
    host = os.environ.get("QDRANT_HOST")
    if not host:
        import socket
        try:
            socket.gethostbyname("qdrant")
            host = "qdrant"
        except socket.gaierror:
            host = "localhost"
    port = int(os.environ.get("QDRANT_PORT", "6333"))
    print(f"Connecting to Qdrant at {host}:{port} ...")
    client = QdrantClient(host=host, port=port)
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            collections = client.get_collections().collections
            break
        except Exception as e:
            if attempt == max_retries:
                print(f"[-] Could not connect to Qdrant after {max_retries} attempts.")
                raise e
            print(f"[*] Waiting for Qdrant to accept connections (attempt {attempt}/{max_retries})...")
            time.sleep(2)

    if any(c.name == COLLECTION for c in collections):
        client.delete_collection(collection_name=COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    rng = random.Random(seed)
    meta = generate_qdrant_points(seed)
    struct_points = []
    for p in meta:
        vector = [rng.random() for _ in range(VECTOR_SIZE)]
        struct_points.append(PointStruct(
            id=p["id"], vector=vector,
            payload={"text": p["text"], "severity": p["severity"]},
        ))
    client.upsert(collection_name=COLLECTION, points=struct_points)

    print("======================================================")
    print(f"[+] Successfully seeded points into '{COLLECTION}' with seed {seed}.")
    print(f"Inspect: http://localhost:6333/collections/{COLLECTION}")
    print("======================================================")


if __name__ == "__main__":
    main()
