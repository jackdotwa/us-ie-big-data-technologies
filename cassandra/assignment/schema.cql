-- Create the keyspace for wind turbine data if it doesn't already exist.
-- SimpleStrategy is used for single-node development clusters.
CREATE KEYSPACE IF NOT EXISTS wind_turbine_data
  WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };


-- Create a table to store time-series sensor readings for each turbine.
-- By specifying `wind_turbine_data.sensor_readings`, we don't need to rely on a `USE` statement.
-- The primary key is partitioned by turbine_id and day to group data logically.
-- Data within a partition is clustered (sorted) by timestamp in descending order.
CREATE TABLE IF NOT EXISTS wind_turbine_data.sensor_readings (
    turbine_id uuid,
    day text,
    timestamp timestamp,
    wind_speed float,
    power_output float,
    temperature int,
    PRIMARY KEY ((turbine_id, day), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Create a table to quickly look up the latest reading for any turbine on a given day.
-- We explicitly define the keyspace here as well for reliability.
CREATE TABLE IF NOT EXISTS wind_turbine_data.latest_readings (
    day text,
    last_updated timestamp,
    turbine_id uuid,
    PRIMARY KEY (day, last_updated)
) WITH CLUSTERING ORDER BY (last_updated DESC);