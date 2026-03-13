-- Teams Table
CREATE TABLE IF NOT EXISTS teams (
    team_id INT PRIMARY KEY,
    abbreviation VARCHAR(3),
    bullpen_era_rank INT
);

-- Inning Logs for Real-time Monitoring
CREATE TABLE IF NOT EXISTS inning_logs (
    log_id SERIAL PRIMARY KEY,
    game_id INT,
    inning_number INT,
    half VARCHAR(10),
    runs_scored INT,
    baserunners INT,
    batters_faced_total INT,
    game_info VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (game_id, inning_number, half)
);

-- Bet Tracking Table
CREATE TABLE IF NOT EXISTS bet_tracking (
    bet_id SERIAL PRIMARY KEY,
    game_id INT,
    game_info VARCHAR(100),
    system_triggered VARCHAR(50),
    odds_taken INT,
    stake DECIMAL,
    result VARCHAR(10) DEFAULT 'PENDING',
    ai_insight TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dynamic Betting Rules Engine Table
CREATE TABLE IF NOT EXISTS betting_rules (
    rule_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'DRY_RUN', -- 'ACTIVE', 'DRY_RUN', 'INACTIVE'
    conditions_json JSONB NOT NULL,
    action_type VARCHAR(50) DEFAULT 'DISCORD_ALERT',
    action_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default placeholder for Discord Webhook if not exists
INSERT INTO system_settings (setting_key, setting_value) 
VALUES ('discord_webhook_url', 'https://discord.com/api/webhooks/placeholder')
ON CONFLICT (setting_key) DO NOTHING;