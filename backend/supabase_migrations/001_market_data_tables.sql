-- ============================================
-- Market Data Storage Schema
-- Supabase PostgreSQL Migration
-- Version: 1.0
-- Date: 2025-11-02
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================
-- Main Market Data Table (Partitioned)
-- ============================================

CREATE TABLE IF NOT EXISTS market_data_daily (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adjusted_close DECIMAL(12, 4),
    dividend DECIMAL(8, 4) DEFAULT 0,
    split_ratio DECIMAL(8, 4) DEFAULT 1,
    data_source VARCHAR(20) DEFAULT 'alpaca',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, date)
) PARTITION BY RANGE (date);

-- Create partitions for each year (2005-2025)
DO $$
DECLARE
    year_num INTEGER;
    start_date DATE;
    end_date DATE;
    partition_name TEXT;
BEGIN
    FOR year_num IN 2005..2025 LOOP
        start_date := make_date(year_num, 1, 1);
        end_date := make_date(year_num + 1, 1, 1);
        partition_name := 'market_data_daily_' || year_num::TEXT;
        
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF market_data_daily 
             FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
    END LOOP;
END $$;

-- Create indexes on partitioned table
CREATE INDEX IF NOT EXISTS idx_market_data_symbol 
    ON market_data_daily (symbol);

CREATE INDEX IF NOT EXISTS idx_market_data_date 
    ON market_data_daily (date DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_symbol_date 
    ON market_data_daily (symbol, date DESC);

CREATE INDEX IF NOT EXISTS idx_market_data_volume 
    ON market_data_daily (volume) WHERE volume > 1000000;

-- BRIN index for efficient time-series scans
CREATE INDEX IF NOT EXISTS idx_market_data_date_brin 
    ON market_data_daily USING brin (date) WITH (pages_per_range = 128);

-- ============================================
-- Symbol Metadata Table
-- ============================================

CREATE TABLE IF NOT EXISTS symbols (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    exchange VARCHAR(20),
    asset_type VARCHAR(20), -- stock, crypto, forex, etf
    sector VARCHAR(50),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT true,
    is_tradable BOOLEAN DEFAULT true,
    first_trade_date DATE,
    last_update DATE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symbols_active 
    ON symbols (symbol) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_symbols_exchange 
    ON symbols (exchange);

CREATE INDEX IF NOT EXISTS idx_symbols_sector 
    ON symbols (sector) WHERE sector IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_symbols_metadata_gin 
    ON symbols USING gin (metadata);

-- ============================================
-- Intraday Data Table (For Top Symbols)
-- ============================================

CREATE TABLE IF NOT EXISTS market_data_intraday (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    trade_count INTEGER,
    vwap DECIMAL(12, 4),
    timeframe VARCHAR(10), -- 1min, 5min, 15min, 1hour
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, timestamp, timeframe)
) PARTITION BY RANGE (timestamp);

-- Create partitions for current year + next year (monthly)
DO $$
DECLARE
    start_date TIMESTAMPTZ;
    end_date TIMESTAMPTZ;
    partition_name TEXT;
BEGIN
    FOR month_num IN 1..24 LOOP
        start_date := date_trunc('month', NOW()) + (month_num - 12) * INTERVAL '1 month';
        end_date := start_date + INTERVAL '1 month';
        partition_name := 'market_data_intraday_' || to_char(start_date, 'YYYY_MM');
        
        BEGIN
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS %I PARTITION OF market_data_intraday 
                 FOR VALUES FROM (%L) TO (%L)',
                partition_name, start_date, end_date
            );
        EXCEPTION WHEN duplicate_table THEN
            -- Partition already exists
            NULL;
        END;
    END LOOP;
END $$;

CREATE INDEX IF NOT EXISTS idx_intraday_symbol_time 
    ON market_data_intraday (symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_intraday_timeframe 
    ON market_data_intraday (timeframe, timestamp DESC);

-- ============================================
-- Data Sync Tracking
-- ============================================

CREATE TABLE IF NOT EXISTS data_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(20), -- daily, intraday, backfill
    sync_date DATE NOT NULL,
    symbols_updated INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    error_details JSONB,
    duration_seconds INTEGER,
    status VARCHAR(20), -- success, failed, partial
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_log_date 
    ON data_sync_log (sync_date DESC);

CREATE INDEX IF NOT EXISTS idx_sync_log_status 
    ON data_sync_log (status, sync_date DESC);

-- ============================================
-- Materialized Views for Performance
-- ============================================

-- Daily summary with technical indicators
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_summary AS
SELECT 
    symbol,
    date,
    close,
    volume,
    adjusted_close,
    -- Daily returns
    (close - LAG(close) OVER w) / NULLIF(LAG(close) OVER w, 0) * 100 AS daily_return,
    -- Moving averages
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS sma_20,
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 50 PRECEDING AND CURRENT ROW) AS sma_50,
    AVG(close) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 200 PRECEDING AND CURRENT ROW) AS sma_200,
    -- Volume indicators
    AVG(volume) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 20 PRECEDING AND CURRENT ROW) AS avg_volume_20,
    -- Price ranges
    MAX(high) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 52 PRECEDING AND CURRENT ROW) AS high_52week,
    MIN(low) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 52 PRECEDING AND CURRENT ROW) AS low_52week
FROM market_data_daily
WHERE date >= CURRENT_DATE - INTERVAL '3 years'
WINDOW w AS (PARTITION BY symbol ORDER BY date);

CREATE UNIQUE INDEX ON daily_summary (symbol, date);
CREATE INDEX ON daily_summary (date DESC);

-- Market overview (top movers, volume leaders)
CREATE MATERIALIZED VIEW IF NOT EXISTS market_overview AS
SELECT 
    symbol,
    date,
    close,
    volume,
    daily_return,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY daily_return DESC) AS rank_gainers,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY daily_return ASC) AS rank_losers,
    ROW_NUMBER() OVER (PARTITION BY date ORDER BY volume DESC) AS rank_volume
FROM daily_summary
WHERE date >= CURRENT_DATE - INTERVAL '30 days';

CREATE UNIQUE INDEX ON market_overview (symbol, date);
CREATE INDEX ON market_overview (date, rank_gainers) WHERE rank_gainers <= 10;
CREATE INDEX ON market_overview (date, rank_losers) WHERE rank_losers <= 10;

-- ============================================
-- Functions and Triggers
-- ============================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_market_data_timestamp
    BEFORE UPDATE ON market_data_daily
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_symbols_timestamp
    BEFORE UPDATE ON symbols
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Function to get latest price
CREATE OR REPLACE FUNCTION get_latest_price(p_symbol VARCHAR)
RETURNS TABLE (
    symbol VARCHAR,
    date DATE,
    close DECIMAL,
    volume BIGINT,
    change_pct DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        md.symbol,
        md.date,
        md.close,
        md.volume,
        ROUND(((md.close - prev.close) / NULLIF(prev.close, 0) * 100)::numeric, 2) AS change_pct
    FROM market_data_daily md
    LEFT JOIN LATERAL (
        SELECT close 
        FROM market_data_daily 
        WHERE symbol = md.symbol 
          AND date < md.date 
        ORDER BY date DESC 
        LIMIT 1
    ) prev ON true
    WHERE md.symbol = p_symbol
    ORDER BY md.date DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get historical data range
CREATE OR REPLACE FUNCTION get_historical_data(
    p_symbol VARCHAR,
    p_start_date DATE,
    p_end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    date DATE,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT,
    adjusted_close DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        md.date,
        md.open,
        md.high,
        md.low,
        md.close,
        md.volume,
        md.adjusted_close
    FROM market_data_daily md
    WHERE md.symbol = p_symbol
      AND md.date BETWEEN p_start_date AND p_end_date
    ORDER BY md.date ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate simple moving average
CREATE OR REPLACE FUNCTION calculate_sma(
    p_symbol VARCHAR,
    p_period INTEGER DEFAULT 20,
    p_date DATE DEFAULT CURRENT_DATE
)
RETURNS DECIMAL AS $$
DECLARE
    result DECIMAL;
BEGIN
    SELECT AVG(close)::DECIMAL(12, 4)
    INTO result
    FROM (
        SELECT close
        FROM market_data_daily
        WHERE symbol = p_symbol
          AND date <= p_date
        ORDER BY date DESC
        LIMIT p_period
    ) subquery;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Row Level Security (RLS)
-- ============================================

-- Enable RLS on tables
ALTER TABLE market_data_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE symbols ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data_intraday ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sync_log ENABLE ROW LEVEL SECURITY;

-- Public read access for market data
CREATE POLICY "Public read access" ON market_data_daily
    FOR SELECT USING (true);

CREATE POLICY "Public read access" ON symbols
    FOR SELECT USING (true);

CREATE POLICY "Public read access" ON market_data_intraday
    FOR SELECT USING (true);

-- Only service role can write
CREATE POLICY "Service role write" ON market_data_daily
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write" ON symbols
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write" ON market_data_intraday
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role write" ON data_sync_log
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- Statistics and Maintenance
-- ============================================

-- Analyze tables for query optimization
ANALYZE market_data_daily;
ANALYZE symbols;
ANALYZE market_data_intraday;

-- Grant permissions
GRANT SELECT ON market_data_daily TO anon, authenticated;
GRANT SELECT ON symbols TO anon, authenticated;
GRANT SELECT ON market_data_intraday TO anon, authenticated;
GRANT SELECT ON daily_summary TO anon, authenticated;
GRANT SELECT ON market_overview TO anon, authenticated;

GRANT ALL ON market_data_daily TO service_role;
GRANT ALL ON symbols TO service_role;
GRANT ALL ON market_data_intraday TO service_role;
GRANT ALL ON data_sync_log TO service_role;

-- ============================================
-- Monitoring Queries (Save as Views)
-- ============================================

CREATE OR REPLACE VIEW storage_stats AS
SELECT 
    'market_data_daily' AS table_name,
    pg_size_pretty(pg_total_relation_size('market_data_daily')) AS total_size,
    pg_size_pretty(pg_relation_size('market_data_daily')) AS data_size,
    pg_size_pretty(pg_indexes_size('market_data_daily')) AS index_size,
    (SELECT COUNT(*) FROM market_data_daily) AS row_count
UNION ALL
SELECT 
    'market_data_intraday',
    pg_size_pretty(pg_total_relation_size('market_data_intraday')),
    pg_size_pretty(pg_relation_size('market_data_intraday')),
    pg_size_pretty(pg_indexes_size('market_data_intraday')),
    (SELECT COUNT(*) FROM market_data_intraday)
UNION ALL
SELECT 
    'symbols',
    pg_size_pretty(pg_total_relation_size('symbols')),
    pg_size_pretty(pg_relation_size('symbols')),
    pg_size_pretty(pg_indexes_size('symbols')),
    (SELECT COUNT(*) FROM symbols);

CREATE OR REPLACE VIEW data_freshness AS
SELECT 
    symbol,
    MAX(date) AS last_update,
    CURRENT_DATE - MAX(date) AS days_stale
FROM market_data_daily
GROUP BY symbol
HAVING CURRENT_DATE - MAX(date) > 1
ORDER BY days_stale DESC
LIMIT 100;

-- ============================================
-- Maintenance Procedures
-- ============================================

-- Refresh materialized views (run daily after market close)
CREATE OR REPLACE FUNCTION refresh_market_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY market_overview;
    
    -- Log refresh
    INSERT INTO data_sync_log (sync_type, sync_date, status)
    VALUES ('view_refresh', CURRENT_DATE, 'success');
END;
$$ LANGUAGE plpgsql;

-- Vacuum and analyze (run weekly)
CREATE OR REPLACE FUNCTION maintain_tables()
RETURNS void AS $$
BEGIN
    VACUUM ANALYZE market_data_daily;
    VACUUM ANALYZE market_data_intraday;
    VACUUM ANALYZE symbols;
    
    -- Log maintenance
    INSERT INTO data_sync_log (sync_type, sync_date, status)
    VALUES ('maintenance', CURRENT_DATE, 'success');
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Migration Complete
-- ============================================

COMMENT ON TABLE market_data_daily IS 'Daily OHLCV data for all tradable symbols, partitioned by year';
COMMENT ON TABLE market_data_intraday IS 'Intraday data for top symbols, partitioned by month';
COMMENT ON TABLE symbols IS 'Symbol metadata and trading information';
COMMENT ON TABLE data_sync_log IS 'Track data synchronization and backfill operations';
COMMENT ON MATERIALIZED VIEW daily_summary IS 'Pre-calculated technical indicators and moving averages';
COMMENT ON MATERIALIZED VIEW market_overview IS 'Top gainers, losers, and volume leaders';

SELECT 'Market data schema created successfully!' AS status;

