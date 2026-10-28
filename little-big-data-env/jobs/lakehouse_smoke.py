"""Lakehouse smoke test: proves the stack can read raw files from S3 and keep Iceberg tables there.

    docker compose -f little-big-data-env/docker-compose.yml exec lakehouse-driver \
        spark-submit /opt/lakehouse/jobs/lakehouse_smoke.py

Reads raw sales CSV from the landing bucket, writes and reads back an Iceberg table in the
warehouse bucket and Parquet in the output bucket, then deletes both again: it leaves only its
event log in the logs bucket.
It uses the fixed configuration only: nothing here sets memory, cores or cluster options.
"""

import time

from pyspark.sql import SparkSession, functions as F, types as T

SALES = T.StructType([T.StructField(c, T.StringType()) for c in [
    "receipt_id", "line_no", "t_dat", "txn_ts", "store_id", "pos_id", "customer_id",
    "sku_id", "article_id", "size", "price", "sales_channel_id", "ingest_id", "promo_code"]])


def main():
    t0 = time.time()
    spark = SparkSession.builder.appName("lakehouse-smoke").getOrCreate()
    sc = spark.sparkContext
    print(f"[*] application {sc.applicationId}, master {sc.master}")
    time.sleep(3)
    executors = sc._jsc.sc().getExecutorMemoryStatus().size() - 1
    print(f"[*] executors registered: {executors}")

    sales = (spark.read.option("header", True).schema(SALES)
             .csv("s3a://landing/drop=*/store=*/sales_*.csv.gz"))
    daily = (sales.groupBy("store_id", F.substring("t_dat", 1, 10).alias("t_dat"))
             .agg(F.count("*").alias("lines")))
    n_rows = sales.count()
    print(f"[+] read {n_rows:,} raw sales rows from landing")

    spark.sql("CREATE NAMESPACE IF NOT EXISTS lake.smoke")
    daily.writeTo("lake.smoke.daily_lines").using("iceberg").createOrReplace()
    back = spark.table("lake.smoke.daily_lines").agg(F.sum("lines")).first()[0]
    snaps = spark.sql("SELECT count(*) FROM lake.smoke.daily_lines.snapshots").first()[0]
    print(f"[+] Iceberg table lake.smoke.daily_lines: {back:,} lines, {snaps} snapshot(s)")
    assert back == n_rows, "Iceberg read-back does not match"

    daily.write.mode("overwrite").parquet("s3a://output/smoke/daily_lines")
    print(f"[+] wrote Parquet to s3a://output/smoke/daily_lines "
          f"({spark.read.parquet('s3a://output/smoke/daily_lines').count():,} rows)")

    # Leave the buckets as they were: only the event log stays.
    # The catalog is file-based: a namespace is a folder, so deleting the folder drops it.
    spark.sql("DROP TABLE lake.smoke.daily_lines PURGE")
    Path, conf = sc._jvm.org.apache.hadoop.fs.Path, sc._jsc.hadoopConfiguration()
    for folder in ("s3a://warehouse/iceberg/smoke", "s3a://output/smoke"):
        Path(folder).getFileSystem(conf).delete(Path(folder), True)
    print("[+] removed lake.smoke and s3a://output/smoke")

    app = sc.applicationId
    spark.stop()
    print(f"[✓] smoke test passed in {time.time() - t0:.0f}s; event log: s3a://logs/spark-events/{app}")


if __name__ == "__main__":
    main()
