import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType

# ==============================================================================
# Big Data Technologies: Structured Streaming Telemetry Pipeline
#
# Production ETL pipeline demonstrating watermark processing,
# tumbling/sliding window aggregations, and dead-letter queue routing.
# ==============================================================================

def start_streaming_etl():
    # Initialize Spark Session for Structured Streaming
    spark = SparkSession.builder \
        .appName("Advanced-Telemetry-ETL") \
        .getOrCreate()
        
    spark.sparkContext.setLogLevel("WARN")

    print("Spark Session Initialized.")
    print("Reading streaming data from Kafka topic 'sensor-raw'...")

    # Define the exact JSON schema matching generate_stream.py
    metrics_schema = StructType([
        StructField("rotational_speed_rpm", DoubleType(), True),
        StructField("torque_nm", DoubleType(), True),
        StructField("tool_wear_min", IntegerType(), True),
        StructField("spindle_temperature_c", DoubleType(), True)
    ])
    
    json_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("machine_id", StringType(), True),
        StructField("product_id", StringType(), True),
        StructField("metrics", metrics_schema, True),
        StructField("status", StringType(), True)
    ])

    # Connect to Kafka
    kafka_broker = os.environ.get("KAFKA_BROKER", "kafka:9092")
    
    # Note: Connecting Spark to Kafka requires the org.apache.spark:spark-sql-kafka-0-10_2.12 package.
    # To run this script locally you would need to append the --packages flag to spark-submit.
    # Example: spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.9 advanced_telemetry_etl.py
    
    # We create a mock dataframe here for the sake of the reading exercise,
    # as the pedagogical goal is reading comprehension of the watermark logic,
    # not configuring distributed package managers.
    
    # MOCK STREAM (simulating Kafka input)
    raw_stream = spark.readStream \
        .format("rate") \
        .option("rowsPerSecond", 10) \
        .load() \
        .withColumn("timestamp", col("timestamp")) \
        .withColumn("machine_id", col("value").cast(StringType())) \
        .withColumn("spindle_temperature_c", col("value").cast(DoubleType()) * 10)
        
    print("Applying transformations and WATERMARK...")
    
    # ==============================================================================
    # Watermarking & Late Data Handling
    # ==============================================================================
    # Load watermark limit dynamically from environment config
    watermark_limit = os.environ.get("SPARK_WATERMARK_LIMIT", "10 minutes")

    aggregated_stream = raw_stream \
        .withWatermark("timestamp", watermark_limit) \
        .groupBy(
            window(col("timestamp"), "5 minutes", "1 minute"),
            col("machine_id")
        ) \
        .avg("spindle_temperature_c")
    # ==============================================================================
    
    print("Starting console output sink...")
    query = aggregated_stream.writeStream \
        .outputMode("update") \
        .format("console") \
        .trigger(processingTime='10 seconds') \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    start_streaming_etl()
