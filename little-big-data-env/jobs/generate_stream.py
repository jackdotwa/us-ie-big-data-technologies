import os
import sys
import time
import json
import uuid
import random
import subprocess
from datetime import datetime

# ==============================================================================
# Dependency Management
# Automatically install kafka-python if missing.
# ==============================================================================
try:
    import sys
    sys.path.insert(0, "/tmp/site-packages")
    from kafka import KafkaProducer
except ImportError:
    print("Kafka-python library not found. Installing to /tmp/site-packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kafka-python", "--target", "/tmp/site-packages"])
    import importlib
    importlib.invalidate_caches()
    from kafka import KafkaProducer

# ==============================================================================
# Data Generation Assumptions (Based on AI4I 2020 Predictive Maintenance Dataset)
# Reference: https://archive.ics.uci.edu/ml/datasets/AI4I+2020+Predictive+Maintenance+Dataset
# 
# The AI4I 2020 dataset is a synthetic dataset that reflects real predictive 
# maintenance data encountered in industry. We use the following ranges:
# 
# 1. Product ID: L (Low, 50%), M (Medium, 30%), H (High, 20%) variant.
# 2. Rotational Speed [rpm]: Centered around 1400-2800 RPM.
# 3. Torque [Nm]: Normally distributed around 40 Nm (StdDev: 10 Nm).
# 4. Tool Wear [min]: Cumulative milling time.
# 5. Spindle Temperature [°C]: The AI4I dataset uses Process/Air temp in Kelvin (~310K).
#    To model critical thermal operating envelopes where spindle head friction 
#    exceeds nominal safety tolerance (> 85°C), we scale this specific metric 
#    to represent direct spindle-head temperature in Celsius (simulating a 
#    Heat Dissipation Failure scenario).
# ==============================================================================

import socket

def get_default_broker():
    """Resolve Kafka broker host automatically via network lookup."""
    try:
        socket.gethostbyname("kafka")
        return "kafka:9092"
    except socket.gaierror:
        return "localhost:9092"

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", get_default_broker())
TOPIC_NAME = "sensor-raw"

def generate_telemetry_event(tool_wear_tracker):
    """Generates a single synthetic AI4I-styled JSON telemetry event."""
    
    # Randomly assign a product quality variant
    variant_roll = random.random()
    if variant_roll < 0.20:
        product_type = "H" # High quality
        wear_increment = 5
    elif variant_roll < 0.50:
        product_type = "M" # Medium quality
        wear_increment = 3
    else:
        product_type = "L" # Low quality
        wear_increment = 2
        
    product_id = f"{product_type}{random.randint(10000, 99999)}"
    machine_id = f"CNC-MILL-{random.randint(1, 5):02d}"
    
    # Base physics simulation
    base_rpm = random.gauss(1500, 100)
    base_torque = random.gauss(40, 10)
    
    # Track cumulative wear per machine
    current_wear = tool_wear_tracker.get(machine_id, 0)
    current_wear += wear_increment
    tool_wear_tracker[machine_id] = current_wear
    
    # Simulate Heat Dissipation Failure (HDF) or friction heat if wear is high
    # Nominal temperature is ~65 C. 
    # If tool wear exceeds 200 mins, friction causes severe temperature spikes > 85 C.
    temp_celsius = random.gauss(65, 5)
    if current_wear > 200 and random.random() > 0.7:
        temp_celsius = random.gauss(88, 3) # Simulate thermal safety limit breach
        
    # Reset tool wear if it gets too high (simulating a tool replacement)
    if current_wear > 240:
        tool_wear_tracker[machine_id] = 0

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "machine_id": machine_id,
        "product_id": product_id,
        "metrics": {
            "rotational_speed_rpm": round(base_rpm, 2),
            "torque_nm": round(max(0, base_torque), 2), # Torque can't be negative
            "tool_wear_min": current_wear,
            "spindle_temperature_c": round(temp_celsius, 2)
        },
        "status": "ACTIVE"
    }
    
    return event

import argparse

def main():
    parser = argparse.ArgumentParser(description="Synthetic factory telemetry stream generator.")
    parser.add_argument(
        "--rate",
        type=float,
        default=10.0,
        help="Target number of telemetry events to generate per second (default: 10.0)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for deterministic generation."
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="Maximum number of events to generate before automatically stopping."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="sensor-raw",
        help="Target Kafka topic to publish to (default: sensor-raw)"
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"Random seed set to {args.seed} for deterministic output.")
    else:
        print("[NOTICE] No --seed specified. Stream output will be non-deterministic.")

    topic_name = args.topic

    print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(f"Successfully connected! Streaming data to topic '{topic_name}' at {args.rate} Hz...")
    print("Press Ctrl+C to stop.")
    print("-" * 50)
    
    tool_wear_tracker = {}
    events_sent = 0
    start_time = time.time()
    
    # Calculate target tick interval
    tick_interval = 1.0 / args.rate if args.rate > 0 else 0.1
    
    try:
        while True:
            start_tick = time.perf_counter()
            event = generate_telemetry_event(tool_wear_tracker)
            producer.send(topic_name, value=event)
            events_sent += 1
            
            # Print to console every 10% of rate or at least 50 events so the student sees activity
            print_interval = max(50, int(args.rate * 5))
            if events_sent % print_interval == 0:
                elapsed_seconds = int(time.time() - start_time)
                print(f"[{datetime.now().strftime('%H:%M:%S')} - Running: {elapsed_seconds}s] Sent {events_sent} events... "
                      f"Sample Temp: {event['metrics']['spindle_temperature_c']}°C (Machine: {event['machine_id']})")
            
            if args.max_events and events_sent >= args.max_events:
                print(f"\nReached maximum event limit ({args.max_events}). Stopping generator.")
                break

            # High precision timing to maintain target rate under system load
            # If rate is very high (e.g. 1000+), we might skip sleep to maximize throughput
            if args.rate < 1000:
                elapsed = time.perf_counter() - start_tick
                sleep_time = max(0, tick_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    finally:
        producer.flush()
        producer.close()
        elapsed_total = int(time.time() - start_time)
        print(f"Total events streamed: {events_sent} over {elapsed_total} seconds")

if __name__ == "__main__":
    main()
