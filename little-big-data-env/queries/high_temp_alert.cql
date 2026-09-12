-- ==============================================================================
-- High-Temperature Sensor Alert Query
-- 
-- Context: The plant maintenance engineer has reported potential cooling failures
--          on milling machines. This query is designed to retrieve telemetry
--          logs where the spindle temperature exceeds 85.0 °C so maintenance
--          can schedule emergency machine isolation.
--
-- Task: Review the keyspace schema in 'queries/init_cassandra.cql' and run
--       this query inside the Cassandra 'cqlsh' console to extract target events.
-- ==============================================================================

SELECT * 
FROM factory_telemetry.sensor_readings 
WHERE spindle_temperature_c > 85.0;
