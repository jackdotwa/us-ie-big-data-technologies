#!/usr/bin/env python3
"""
Task 4: Physical Storage Mechanics — Row Store (Postgres) vs. Vectorized Columnar (DuckDB)
Executes identical 7-day multi-column feature extraction workloads across both engines.
Measures buffer page examination, projection pruning, query latencies, and speedup ratio.
"""

import sys
import os
import time
import psycopg2
import duckdb

def benchmark_storage_showdown(student_nr: int, db_path: str = "factory_telemetry.duckdb"):
    print("=========================================================================")
    print(f" TASK 4: STORAGE MECHANICS SHOWDOWN — POSTGRES HEAP VS. DUCKDB COLUMNAR")
    print("=========================================================================\n")
    
    # 1. PostgreSQL Row-Store Feature Extraction
    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = int(os.getenv("PGPORT", "5432"))
    pg_user = os.getenv("PGUSER", "postgres")
    pg_pass = os.getenv("PGPASSWORD", "postgres")
    pg_db = os.getenv("PGDATABASE", "bdt_db")

    print(f"[*] Benchmarking PostgreSQL Row-Store (obt_sensor_events on port {pg_port})...")
    try:
        pg_conn = psycopg2.connect(dbname=pg_db, user=pg_user, password=pg_pass, host=pg_host, port=pg_port)
    except Exception as e:
        if pg_port == 5432:
            print(f"[-] Port 5432 failed ({e}), trying fallback port 5433...")
            pg_port = 5433
            pg_conn = psycopg2.connect(dbname=pg_db, user=pg_user, password=pg_pass, host=pg_host, port=5433)
        else:
            raise e
    pg_cur = pg_conn.cursor()
    
    pg_query = """
    EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
    SELECT timestamp, air_temp_k, process_temp_k, rotational_speed_rpm, torque_nm
    FROM obt_sensor_events
    WHERE equipment_id = 12 AND timestamp BETWEEN '2026-01-01 00:00:00' AND '2026-01-07 00:00:00'
    ORDER BY timestamp DESC;
    """
    
    pg_times = []
    for _ in range(5):
        t0 = time.time()
        pg_cur.execute(pg_query)
        pg_times.append((time.time() - t0) * 1000.0)
        explain_json = pg_cur.fetchone()[0]
        
    pg_latency = sorted(pg_times)[len(pg_times) // 2]
    plan = explain_json[0]["Plan"]
    shared_read = plan.get("Shared Read Blocks", 0)
    shared_hit = plan.get("Shared Hit Blocks", 0)
    total_blocks = shared_read + shared_hit
    hit_ratio = (shared_hit / total_blocks * 100.0) if total_blocks > 0 else 100.0
    
    print(f"    - Median Latency: {pg_latency:.2f} ms")
    print(f"    - Physical Disk Blocks Examined: {total_blocks} (Hit Ratio: {hit_ratio:.1f}%)")
    pg_cur.close()
    pg_conn.close()
    
    # 2. DuckDB Vectorized Columnar Feature Extraction
    print("\n[*] Benchmarking DuckDB Vectorized Columnar Store (obt_columnar)...")
    con = duckdb.connect(db_path, read_only=True)
    con.execute("PRAGMA threads=4;")
    
    duck_query = """
    SELECT timestamp, air_temp_k, process_temp_k, rotational_speed_rpm, torque_nm
    FROM obt_columnar
    WHERE equipment_id = 12 AND timestamp BETWEEN '2026-01-01 00:00:00' AND '2026-01-07 00:00:00'
    ORDER BY timestamp DESC;
    """
    
    duck_times = []
    for _ in range(10):
        t0 = time.time()
        rows = con.execute(duck_query).fetchall()
        duck_times.append((time.time() - t0) * 1000.0)
        
    duck_latency = sorted(duck_times)[len(duck_times) // 2]
    print(f"    - Median Latency: {duck_latency:.2f} ms")
    print(f"    - Target Rows Retrieved: {len(rows)}")
    con.close()
    
    # Speedup ratio
    speedup = pg_latency / duck_latency if duck_latency > 0 else 1.0
    print("\n=========================================================================")
    print(" SUMMARY METRICS:")
    print(f"    - PostgreSQL Row-Store Latency: {pg_latency:.2f} ms")
    print(f"    - DuckDB Columnar Latency:     {duck_latency:.2f} ms")
    print(f"    - Measured Speedup Ratio:      {speedup:.2f}x")
    print("=========================================================================")
    return speedup

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit("Usage: python3 columnar-usecases/duckdb-factory-analytics/benchmark_row_vs_columnar.py <YOUR_STUDENT_NUMBER> [factory_telemetry.duckdb]")
    student_nr = int(sys.argv[1])
    db_file = sys.argv[2] if len(sys.argv) > 2 else "factory_telemetry.duckdb"
    benchmark_storage_showdown(student_nr, db_file)
