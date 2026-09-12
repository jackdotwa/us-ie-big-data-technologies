-- Postgres Seed Script: Trivial Canary Dataset (Industrial Sensor & Maintenance Logs)
-- Target Grain: 2 Equipment Masters, 2 Maintenance Logs, 5 Raw Sensor Events

-- 1. equipment_master (2 machines)
CREATE TABLE IF NOT EXISTS equipment_master (
    equipment_id INT PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    plant_location VARCHAR(50) NOT NULL
);

INSERT INTO equipment_master (equipment_id, equipment_type, plant_location) VALUES
(1, 'CNC_MILL_A', 'PLANT_1'),
(2, 'CNC_MILL_B', 'PLANT_1');

-- 2. maintenance_logs (2 logs - both for equipment_id = 1)
CREATE TABLE IF NOT EXISTS maintenance_logs (
    log_id INT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    maintenance_date TIMESTAMP NOT NULL,
    action_taken VARCHAR(100) NOT NULL
);

INSERT INTO maintenance_logs (log_id, equipment_id, maintenance_date, action_taken) VALUES
(101, 1, '2026-01-01 08:00:00', 'OIL_CHANGE'),
(102, 1, '2026-01-05 10:00:00', 'BELT_REPLACEMENT');

-- 3. raw_sensor_events (5 events)
CREATE TABLE IF NOT EXISTS raw_sensor_events (
    event_id BIGINT PRIMARY KEY,
    equipment_id INT REFERENCES equipment_master(equipment_id),
    timestamp TIMESTAMP NOT NULL,
    temperature NUMERIC(5, 2) NOT NULL,
    vibration NUMERIC(5, 2) NOT NULL,
    alarm_code VARCHAR(20)
);

INSERT INTO raw_sensor_events (event_id, equipment_id, timestamp, temperature, vibration, alarm_code) VALUES
(1, 1, '2026-01-10 00:00:01', 25.0, 0.12, NULL),
(2, 1, '2026-01-10 00:00:02', 26.5, 0.15, NULL),
(3, 1, '2026-01-10 00:00:03', 27.0, 0.18, 'ALARM_HEAT'),
(4, 2, '2026-01-10 00:00:01', 30.0, 0.05, NULL),
(5, 2, '2026-01-10 00:00:02', 31.0, 0.08, NULL);
