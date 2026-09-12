#!/usr/bin/env python3
import os
import sys
import time
import json

# Add parent directory to path so we can import from jobs
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "jobs"))
from generate_stream import generate_telemetry_event

def main():
    print("======================================================")
    print("    BDT Live Telemetry Stream Inspector (Offline)      ")
    print("======================================================")
    print("This utility runs the raw mathematical physics engine")
    print("from 'generate_stream.py' locally without connecting")
    print("to a Kafka broker. Use this to verify payload schemas.")
    print("Press Ctrl+C to stop.")
    print("======================================================\n")
    
    # Track tool wear per machine locally to model cumulative friction
    tool_wear_tracker = {}
    event_count = 0
    
    try:
        while True:
            event = generate_telemetry_event(tool_wear_tracker)
            event_count += 1
            
            print(f"--- [Event #{event_count}] ---")
            print(json.dumps(event, indent=2))
            print("-" * 54)
            
            time.sleep(1.0) # Print 1 event per second
            
    except KeyboardInterrupt:
        print("\n\nStream inspection terminated by user.")

if __name__ == "__main__":
    main()
