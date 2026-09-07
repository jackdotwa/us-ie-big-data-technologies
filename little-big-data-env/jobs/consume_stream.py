import os
import sys
import time
import json
import socket
import subprocess

# ==============================================================================
# Dependency Management
# Automatically install kafka-python if missing.
# ==============================================================================
try:
    sys.path.insert(0, "/tmp/site-packages")
    from kafka import KafkaConsumer
except ImportError:
    print("Kafka-python library not found. Installing to /tmp/site-packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python", "--target", "/tmp/site-packages"])
    import importlib
    importlib.invalidate_caches()
    from kafka import KafkaConsumer

def get_default_broker():
    """Resolve Kafka broker host automatically via network lookup."""
    try:
        socket.gethostbyname("kafka")
        return "kafka:9092"
    except socket.gaierror:
        return "localhost:9092"

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", get_default_broker())
TOPIC_NAME = "sensor-raw"
CONSUMER_GROUP = "telemetry-ingest-group"
TARGET_CONSUME_RATE = 1.67 # Target consumption rate (Hz) for telemetry ingestion

def main():
    print(f"Connecting to Kafka broker at {KAFKA_BROKER} as group '{CONSUMER_GROUP}'...")
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        group_id=CONSUMER_GROUP,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        auto_commit_interval_ms=1000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"Successfully connected! Throttled ingestion active at {TARGET_CONSUME_RATE} Hz...")
    print("Press Ctrl+C to stop.")
    print("-" * 50)

    events_consumed = 0
    tick_interval = 1.0 / TARGET_CONSUME_RATE
    
    try:
        for message in consumer:
            start_tick = time.perf_counter()
            events_consumed += 1
            
            if events_consumed % 50 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] Consumed {events_consumed} events... "
                      f"Current offset: {message.offset} (Partition: {message.partition})")
            
            # High precision timing to maintain target rate under system load
            elapsed = time.perf_counter() - start_tick
            sleep_time = max(0, tick_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        consumer.close()
        print(f"Total events consumed: {events_consumed}")

if __name__ == "__main__":
    main()
