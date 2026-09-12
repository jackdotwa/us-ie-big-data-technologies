import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand

def run_baseline_job():
    print("Initializing Spark Session...")
    
    # In a real environment, memory would be injected via config/pipeline_rules.env
    # To avoid restarting Docker, dynamically load configuration at runtime.
    env_path = "/opt/spark/work-dir/config/pipeline_rules.env"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.split("#")[0].strip()
                    
    executor_memory = os.environ.get("SPARK_EXECUTOR_MEMORY", "1g")
    
    spark = SparkSession.builder \
        .appName("BDT-Baseline-Telemetry-Job") \
        .config("spark.executor.memory", executor_memory) \
        .config("spark.driver.memory", "512m") \
        .getOrCreate()

    print(f"Spark Session initialized. Master: {spark.sparkContext.master}")
    print(f"Tracking UI available at: http://localhost:4040")
    print("--------------------------------------------------")
    
    # Generate synthetic workload dataset
    batch_size = int(os.environ.get("BATCH_SIZE", "1000000"))
    
    print(f"Generating synthetic telemetry data with {batch_size} rows...")
    df = spark.range(0, batch_size).withColumn("sensor_val", rand() * 100)
    
    print("Executing aggregation...")
    summary_df = df.groupBy(col("id") % 10).avg("sensor_val")
    summary_df.show()
    
    print("--------------------------------------------------")
    print("Job completed successfully!")
    print("Keeping the Spark UI alive for telemetry inspection - press Ctrl+C/Cmd+C to quit...")
    print("Navigate to http://localhost:4040 and check the 'Executors' tab.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Spark Session...")
    finally:
        spark.stop()

if __name__ == "__main__":
    run_baseline_job()
