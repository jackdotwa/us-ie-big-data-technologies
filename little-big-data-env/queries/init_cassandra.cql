CREATE KEYSPACE IF NOT EXISTS factory_telemetry 
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

CREATE TABLE IF NOT EXISTS factory_telemetry.sensor_readings (
    machine_id text,
    event_id uuid,
    timestamp timestamp,
    product_id text,
    spindle_temperature_c double,
    status text,
    PRIMARY KEY (machine_id, event_id)
);
