import os
import time
import uuid
from datetime import datetime, timedelta
import random 
import logging
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, BatchStatement


log = logging.getLogger(__name__)
rnd = random.Random()
rnd.seed(123) # do not change - needed for marking

def load(session):

    # --- Data Loading Logic ---
    log.info("\n--- Populating database with synthetic data ---")

    # Prepare insert statements
    insert_sensor_statement = session.prepare("INSERT INTO wind_turbine_data.sensor_readings (turbine_id, day, timestamp, wind_speed, power_output, temperature) VALUES (?, ?, ?, ?, ?, ?)")
    insert_latest_statement = session.prepare("INSERT INTO wind_turbine_data.latest_readings (day, last_updated, turbine_id) VALUES (?, ?, ?)")


    turbine_ids = [uuid.UUID(int=rnd.getrandbits(128), version=4) for _ in range(5)]
    start_date = datetime.now() - timedelta(days=5)

    # Generate and insert data
    total_records = 0
    for day_offset in range(5):
        current_date = start_date + timedelta(days=day_offset)
        day_str = current_date.strftime('%Y-%m-%d')
        
        for turbine_id in turbine_ids:
            batch = BatchStatement()
            for minute_offset in range(0, 1440, 15): 
                timestamp = current_date + timedelta(minutes=minute_offset)
                wind_speed = round(random.uniform(5.0, 30.0), 2)
                power_output = round(wind_speed * 100 + random.uniform(-50.0, 50.0), 2)
                if power_output < 0:
                    power_output = 0
                temperature = random.randint(5, 35)

                day_str = timestamp.strftime('%Y-%m-%d')
                log.info((turbine_id, day_str, timestamp, wind_speed, power_output, temperature))
                # Add both inserts to the batch
                batch.add(insert_sensor_statement, (turbine_id, day_str, timestamp, wind_speed, power_output, temperature))
                batch.add(insert_latest_statement, (day_str, timestamp, turbine_id))
                total_records += 1
            session.execute(batch)

    log.info(f"✅ Data loading complete. Inserted {total_records} records.")

