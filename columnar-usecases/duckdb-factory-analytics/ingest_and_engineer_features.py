#!/usr/bin/env python3
"""
Task 3: In-Process Columnar Analytics (DuckDB)
Ingests 5,000,000 OBT records from PostgreSQL into native DuckDB columnar storage,
then computes per-machine feature aggregations.
"""

import sys
import os
import time
import duckdb

def run_task3_duckdb(student_nr: int, db_path: str = "factory_telemetry.duckdb"):
    print("=========================================================================")
    print(f" TASK 3: VECTORIZED COLUMNAR FEATURE SERVING (Student: {student_nr})")
    print("=========================================================================\n")

    # Connect to native DuckDB database file
    con = duckdb.connect(db_path)
    con.execute("PRAGMA threads=4;")

    # 1. Install & load PostgreSQL scanner extension
    print("[*] Initializing DuckDB PostgreSQL scanner...")
    con.execute("INSTALL postgres; LOAD postgres;")

    pg_host = os.getenv("PGHOST", "localhost")
    pg_port = os.getenv("PGPORT", "5432")
    pg_user = os.getenv("PGUSER", "postgres")
    pg_pass = os.getenv("PGPASSWORD", "postgres")
    pg_db = os.getenv("PGDATABASE", "bdt_db")

    pg_conn_str = f"dbname={pg_db} user={pg_user} password={pg_pass} host={pg_host} port={pg_port}"
    print(f"[*] Attaching PostgreSQL feature store ({pg_conn_str})...")
    
    try:
        con.execute(f"ATTACH '{pg_conn_str}' AS pg (TYPE POSTGRES);")
    except Exception as e:
        if pg_port == "5432":
            print(f"[-] Note: Direct attach on port 5432 failed ({e}). Trying fallback port 5433...")
            pg_conn_str = f"dbname={pg_db} user={pg_user} password={pg_pass} host={pg_host} port=5433"
            con.execute(f"ATTACH '{pg_conn_str}' AS pg (TYPE POSTGRES);")
        else:
            raise e

    # 2. Create native columnar table
    print("[*] Ingesting 5,000,000 OBT rows into native DuckDB columnar table (obt_columnar)...")
    t_ingest_start = time.time()
    
    # -------------------------------------------------------------------------
    # TODO 1: Materialize the PostgreSQL OBT into native DuckDB columnar storage
    # Create a native DuckDB table named `obt_columnar` holding every row of
    # the attached PostgreSQL table `pg.obt_sensor_events`.
    # -------------------------------------------------------------------------
    
    ingest_duration = time.time() - t_ingest_start
    try:
        total_rows = con.execute("SELECT count(*) FROM obt_columnar;").fetchone()[0]
    except Exception as e:
        print(f"[-] Error querying obt_columnar: {e}")
        print("    Ensure you implemented TODO 1 to create table `obt_columnar`.")
        return 0, 0.0

    assert total_rows == 5000000, f"Expected 5,000,000 rows in obt_columnar, found {total_rows}"
    print(f"[+] Successfully materialized {total_rows:,} rows into columnar storage in {ingest_duration:.2f}s.")

    # 3. Per-machine feature aggregations
    print("\n[*] Executing vectorized feature extraction across 50 CNC machines...")
    t_feat_start = time.time()
    
    # -------------------------------------------------------------------------
    # TODO 2: Per-machine feature extraction query
    # Return one row per machine, ordered by equipment_id, with the columns:
    #   equipment_id, total_samples, mean_delta_temp, power_volatility_w, total_failures
    # The feature definitions are in the Task 3 section of the brief.
    # -------------------------------------------------------------------------
    query_features = """
        -- TODO: Implement your analytical feature extraction query here
    """
    
    try:
        res = con.execute(query_features).fetchall()
        feat_duration = (time.time() - t_feat_start) * 1000.0
        assert len(res) == 50, f"Expected features for 50 CNC machines, got {len(res)}"
        assert res[0][1] == 100000, f"Expected 100,000 samples per machine, got {res[0][1]}"
    except Exception as e:
        print(f"[-] Feature extraction error: {e}")
        print("    Ensure you implemented TODO 2 to aggregate features across all 50 machines.")
        return total_rows, 0.0

    print(f"[+] Vectorized aggregation completed in {feat_duration:.2f} ms across {len(res)} CNC cells.")
    print("    Sample extracted features (Machines 1-3):")
    for row in res[:3]:
        print(f"    - CNC Cell {row[0]:02d}: Samples={row[1]:,}, Mean ΔT={row[2]} K, Power Volatility={row[3]} W, Failures={row[4]}")

    con.close()
    return total_rows, feat_duration

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit("Usage: python3 columnar-usecases/duckdb-factory-analytics/ingest_and_engineer_features.py <YOUR_STUDENT_NUMBER>")
    student_num = int(sys.argv[1])
    run_task3_duckdb(student_num)

