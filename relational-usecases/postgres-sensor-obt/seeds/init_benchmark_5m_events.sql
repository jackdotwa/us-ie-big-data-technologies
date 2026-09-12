-- Postgres Seed Script: Full Scale Benchmark Dataset (5 Million Sensor Events)
-- Used for EXPLAIN ANALYZE, work_mem disk spill diagnostics, and BRIN index benchmarking.

-- 1. equipment_master (10 distinct machines)
CREATE TABLE IF NOT EXISTS equipment_master (
    equipment_id INT PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    plant_location VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    bloated_manual_text TEXT NOT NULL
);

INSERT INTO equipment_master (equipment_id, equipment_type, plant_location, manufacturer, bloated_manual_text)
SELECT 
    g AS equipment_id,
    'CNC_MILL_' || (g % 5 + 1) AS equipment_type,
    'PLANT_' || (g % 3 + 1) AS plant_location,
    'HAAS_AUTOMATION' AS manufacturer,
    REPEAT('MANUAL_DOC_BLOAT_', 100) AS bloated_manual_text
FROM generate_series(1, 10) g;

-- 2. maintenance_logs (30 logs = 3 per machine)
CREATE TABLE IF NOT EXISTS maintenance_logs (
    log_id INT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    maintenance_date TIMESTAMP NOT NULL,
    action_taken VARCHAR(100) NOT NULL,
    bloated_technician_notes TEXT NOT NULL
);

INSERT INTO maintenance_logs (log_id, equipment_id, maintenance_date, action_taken, bloated_technician_notes)
SELECT 
    g AS log_id,
    ((g - 1) % 10 + 1) AS equipment_id,
    NOW() - (g || ' days')::INTERVAL AS maintenance_date,
    'ROUTINE_INSPECTION_' || g AS action_taken,
    REPEAT('TECHNICIAN_LOG_BLOAT_', 100) AS bloated_technician_notes
FROM generate_series(1, 30) g;

-- 3. raw_sensor_events (200,000 padded rows for local laptop testing)
CREATE TABLE IF NOT EXISTS raw_sensor_events (
    event_id BIGINT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    timestamp TIMESTAMP NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL,
    vibration NUMERIC(5, 2) NOT NULL,
    alarm_code VARCHAR(20),
    bloated_payload TEXT NOT NULL
);

INSERT INTO raw_sensor_events (event_id, equipment_id, timestamp, temperature, vibration, alarm_code, bloated_payload)
SELECT 
    g AS event_id,
    ((g - 1) % 10 + 1) AS equipment_id,
    TIMESTAMP '2026-01-01 00:00:00' + (g || ' seconds')::INTERVAL AS timestamp,
    (20 + (g % 50)::NUMERIC / 2) AS temperature,
    (0.1 + (g % 20)::NUMERIC / 10) AS vibration,
    CASE WHEN g % 100 = 0 THEN 'ALARM_OVERHEAT' ELSE NULL END AS alarm_code,
    REPEAT('RAW_PAYLOAD_BLOAT_', 50) AS bloated_payload
FROM generate_series(1, 200000) g;

CREATE INDEX IF NOT EXISTS idx_raw_sensor_events_timestamp ON raw_sensor_events(timestamp);
