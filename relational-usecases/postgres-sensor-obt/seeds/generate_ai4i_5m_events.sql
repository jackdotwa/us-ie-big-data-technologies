-- Seed Generator for AI4I 2020 CNC Telemetry Benchmark (5,000,000 Rows)
-- Generates realistic equipment master, maintenance logs, and high-frequency sensor readings with bloat.

\if :{?student_nr}
\set seed :student_nr
\else
\echo 'FATAL ERROR: student_nr variable is required.'
\echo 'Usage: psql -v student_nr=<YOUR_STUDENT_NUMBER> -f generate_ai4i_5m_events.sql'
\q
\endif

DROP TABLE IF EXISTS raw_sensor_events CASCADE;
DROP TABLE IF EXISTS maintenance_logs CASCADE;
DROP TABLE IF EXISTS equipment_master CASCADE;
DROP TABLE IF EXISTS obt_sensor_events CASCADE;
DROP TABLE IF EXISTS pb1_meta CASCADE;

CREATE TABLE pb1_meta (
    student_nr VARCHAR(50) PRIMARY KEY,
    is_buffered BOOLEAN NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO pb1_meta (student_nr, is_buffered)
VALUES (:'seed'::TEXT, ((:seed % 2) != 0));

-- 1. equipment_master (50 CNC milling machines)
CREATE TABLE equipment_master (
    equipment_id INT PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    plant_location VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    spec_sheet_blob TEXT NOT NULL
);

INSERT INTO equipment_master (equipment_id, equipment_type, plant_location, manufacturer, spec_sheet_blob)
SELECT 
    g AS equipment_id,
    'CNC_5AXIS_MILL_' || LPAD(g::TEXT, 2, '0') AS equipment_type,
    'STELLENBOSCH_PLANT_' || (g % 3 + 1) AS plant_location,
    'HAAS_AUTOMATION' AS manufacturer,
    REPEAT(MD5((g + :seed)::TEXT), 8) || ' | SPEC_SHEET_PDF_BINARY_REFERENCE_URI' AS spec_sheet_blob
FROM generate_series(1, 50) g;

-- 2. maintenance_logs (250 maintenance records = 5 per machine across the 11.6-day sensor window)
CREATE TABLE maintenance_logs (
    log_id INT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    maintenance_date TIMESTAMP NOT NULL,
    action_taken VARCHAR(100) NOT NULL,
    technician_notes TEXT NOT NULL
);

INSERT INTO maintenance_logs (log_id, equipment_id, maintenance_date, action_taken, technician_notes)
SELECT 
    g AS log_id,
    ((g - 1) % 50 + 1) AS equipment_id,
    TIMESTAMP '2026-01-01 00:00:00' + (
        ((((g - 1) / 50) * 52) + (((g - 1) % 50) * 0.8) + ((:seed % 17) * 0.1)) || ' hours'
    )::INTERVAL AS maintenance_date,
    CASE (g % 4)
        WHEN 0 THEN 'SPINDLE_BEARING_REPLACEMENT'
        WHEN 1 THEN 'LUBRICATION_SYSTEM_FLUSH'
        WHEN 2 THEN 'CUTTING_TOOL_INSERT_INDEXING'
        ELSE 'COOLANT_PRESSURE_VALVE_CALIBRATION'
    END AS action_taken,
    REPEAT(MD5((g * 7 + :seed)::TEXT), 10) || ' | TECHNICIAN_HANDWRITTEN_DIAGNOSTIC_FREE_TEXT_NOTES' AS technician_notes
FROM generate_series(1, 250) g;

-- 3. raw_sensor_events (5,000,000 high-frequency sensor readings, 5 readings/sec across 50 machines = 11.57 days)
CREATE TABLE raw_sensor_events (
    event_id BIGINT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    timestamp TIMESTAMP NOT NULL,
    air_temp_k NUMERIC(5,2) NOT NULL,
    process_temp_k NUMERIC(5,2) NOT NULL,
    rotational_speed_rpm INT NOT NULL,
    torque_nm NUMERIC(5,2) NOT NULL,
    tool_wear_min INT NOT NULL,
    machine_failure INT NOT NULL,
    raw_packet_hex TEXT NOT NULL
);

INSERT INTO raw_sensor_events (
    event_id, equipment_id, timestamp, 
    air_temp_k, process_temp_k, rotational_speed_rpm, 
    torque_nm, tool_wear_min, machine_failure, raw_packet_hex
)
SELECT 
    p AS event_id,
    ((g - 1) % 50 + 1) AS equipment_id,
    TIMESTAMP '2026-01-01 00:00:00' + ((g / 5) || ' seconds')::INTERVAL AS timestamp,
    (298.15 + (SIN((g + (:seed % 1000))::FLOAT / 1200.0) * 2.5) + ((((g * 13 + :seed) % 100)::FLOAT - 50.0) / 100.0))::NUMERIC(5,2) AS air_temp_k,
    (307.50 + (((g - 1) % 50 + 1)::FLOAT * 0.08) + (SIN((g + (:seed % 500))::FLOAT / 400.0) * 1.5) + ((((g * 17 + :seed) % 100)::FLOAT) / 50.0))::NUMERIC(5,2) AS process_temp_k,
    (1500 + (((g * 7 + :seed) % 400) - 200))::INT AS rotational_speed_rpm,
    (40.0 + (((g * 11 + :seed) % 30) - 15)::FLOAT * 0.8)::NUMERIC(5,2) AS torque_nm,
    (((g / 20) + (:seed % 25)) % 250)::INT AS tool_wear_min,
    CASE 
        WHEN ((g + (:seed % 50)) % 1009 = 0) 
             OR ((((g / 20) + (:seed % 25)) % 250) > 220 
                 AND (40.0 + (((g * 11 + :seed) % 30) - 15)::FLOAT * 0.8) > 50.0 
                 AND ((g + :seed) % 73 = 0))
        THEN 1 
        ELSE 0 
    END AS machine_failure,
    REPEAT(MD5(((g + :seed) % 100)::TEXT), 6) || '0xAAFFBEEF01' AS raw_packet_hex
FROM generate_series(1, 5000000) p,
LATERAL (
    SELECT CASE 
        WHEN ((:seed % 2) != 0) THEN (((p - 1) % 100) * 50000 + (p - 1) / 100 + 1)
        ELSE p 
    END AS g
) x;

-- Baseline index only on primary key
ANALYZE equipment_master;
ANALYZE maintenance_logs;
ANALYZE raw_sensor_events;
