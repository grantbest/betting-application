-- Assuming the existence of other required tables and modifications

CREATE TABLE IF NOT EXISTS game_weather (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id),
    temperature DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    conditions VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration Note: If there is existing weather data structure, use appropriate SQL commands to migrate data without loss.
-- Example:
-- ALTER TABLE existing_weather_table RENAME TO old_weather_table;
-- INSERT INTO game_weather (game_id, temperature, wind_speed, conditions, timestamp)
--     SELECT game_id, temperature, wind_speed, conditions, timestamp FROM old_weather_table;
-- DROP TABLE old_weather_table;