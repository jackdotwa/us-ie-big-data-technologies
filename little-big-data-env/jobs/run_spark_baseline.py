import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, rand

def run_baseline_job():
    print("Initializing Spark Session...")
    
    # In a real environment, memory would be injected via config/pipeline_rules.env
    # We dynamically load it here so students don't need to restart Docker
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
    
    # Generate a dummy dataframe to simulate workload
    # We will simulate a large dataset that forces shuffles and memory usage
    batch_size = int(os.environ.get("BATCH_SIZE", "1000000"))
    
    print(f"Generating synthetic telemetry data with {batch_size} rows...")
    df = spark.range(0, batch_size).withColumn("sensor_val", rand() * 100)
    
    # Force a shuffle operation
    print("Executing wide transformation (shuffle)...")
    summary_df = df.groupBy(col("id") % 10).avg("sensor_val")
    
    # Action to trigger execution
    summary_df.show()
    
    print("--------------------------------------------------")
    print("Job completed successfully!")
    print("Keeping the Spark UI alive for for telemetry inspection - press Ctrl+C/Cmd+C to quit...")
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
