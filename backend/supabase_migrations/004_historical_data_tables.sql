-- Migration 004: Historical Market Data Storage
-- Purpose: Store OHLCV bars from multiple providers to minimize API calls
-- Architecture: Inspired by TradingView, Webull (database-first approach)
-- Created: 2025-01-29

-- ============================================================================
-- Table 1: historical_bars - Main storage for all price data
-- ============================================================================
CREATE TABLE IF NOT EXISTS historical_bars (
  symbol TEXT NOT NULL,
  interval TEXT NOT NULL,  -- '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo'
  timestamp TIMESTAMPTZ NOT NULL,
  open DECIMAL(12,4) NOT NULL,
  high DECIMAL(12,4) NOT NULL,
  low DECIMAL(12,4) NOT NULL,
  close DECIMAL(12,4) NOT NULL,
  volume BIGINT NOT NULL,
  trade_count INTEGER,
  vwap DECIMAL(12,4),
  data_source TEXT DEFAULT 'alpaca',  -- 'alpaca', 'yahoo', 'cnbc', 'polygon'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (symbol, interval, timestamp)
);

-- Performance indexes (critical for fast queries)
CREATE INDEX IF NOT EXISTS idx_symbol_interval_time
  ON historical_bars(symbol, interval, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_timestamp
  ON historical_bars(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_symbol_interval
  ON historical_bars(symbol, interval);

-- Comment for documentation
COMMENT ON TABLE historical_bars IS 'Stores historical OHLCV candlestick data from various providers. Primary key ensures no duplicate bars.';
COMMENT ON COLUMN historical_bars.interval IS 'Bar timeframe: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo';
COMMENT ON COLUMN historical_bars.data_source IS 'Provider that supplied this data (alpaca, yahoo, etc.)';

-- ============================================================================
-- Table 2: data_coverage - Track what data we have for each symbol/interval
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_coverage (
  symbol TEXT NOT NULL,
  interval TEXT NOT NULL,
  earliest_bar TIMESTAMPTZ,
  latest_bar TIMESTAMPTZ,
  total_bars INTEGER DEFAULT 0,
  last_fetched_at TIMESTAMPTZ DEFAULT NOW(),
  last_api_call TIMESTAMPTZ,
  is_complete BOOLEAN DEFAULT FALSE,  -- Have we fetched all available history?
  max_history_days INTEGER,  -- Maximum days available for this symbol/interval
  PRIMARY KEY (symbol, interval)
);

-- Index for finding stale data
CREATE INDEX IF NOT EXISTS idx_last_api_call
  ON data_coverage(last_api_call DESC);

CREATE INDEX IF NOT EXISTS idx_last_fetched
  ON data_coverage(last_fetched_at DESC);

COMMENT ON TABLE data_coverage IS 'Metadata tracking data completeness for each symbol/interval combination';
COMMENT ON COLUMN data_coverage.is_complete IS 'True if we have fetched all available history from provider';
COMMENT ON COLUMN data_coverage.max_history_days IS 'Maximum days provider offers for this interval (e.g., Yahoo 5m = 60 days, Alpaca = 2555 days)';

-- ============================================================================
-- Table 3: api_call_log - Monitor API usage and performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_call_log (
  id SERIAL PRIMARY KEY,
  provider TEXT NOT NULL,  -- 'alpaca', 'yahoo', 'cnbc', 'polygon'
  endpoint TEXT,
  symbol TEXT,
  interval TEXT,
  start_date TIMESTAMPTZ,
  end_date TIMESTAMPTZ,
  bars_fetched INTEGER DEFAULT 0,
  duration_ms INTEGER,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  http_status INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics and monitoring
CREATE INDEX IF NOT EXISTS idx_provider_created
  ON api_call_log(provider, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_symbol_created
  ON api_call_log(symbol, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_success
  ON api_call_log(success, created_at DESC);

COMMENT ON TABLE api_call_log IS 'Audit log of all external API calls for monitoring rate limits and performance';
COMMENT ON COLUMN api_call_log.duration_ms IS 'API call duration in milliseconds';

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to update data_coverage after inserting bars
CREATE OR REPLACE FUNCTION update_data_coverage()
RETURNS TRIGGER AS $$
BEGIN
  -- Update or insert coverage metadata
  INSERT INTO data_coverage (
    symbol,
    interval,
    earliest_bar,
    latest_bar,
    total_bars,
    last_fetched_at
  )
  VALUES (
    NEW.symbol,
    NEW.interval,
    NEW.timestamp,
    NEW.timestamp,
    1,
    NOW()
  )
  ON CONFLICT (symbol, interval) DO UPDATE SET
    earliest_bar = LEAST(data_coverage.earliest_bar, NEW.timestamp),
    latest_bar = GREATEST(data_coverage.latest_bar, NEW.timestamp),
    total_bars = data_coverage.total_bars + 1,
    last_fetched_at = NOW();

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update coverage on bar insert
CREATE TRIGGER trigger_update_coverage
  AFTER INSERT ON historical_bars
  FOR EACH ROW
  EXECUTE FUNCTION update_data_coverage();

-- ============================================================================
-- Initial Data / Seed
-- ============================================================================

-- No initial data needed - will be populated by pre-warming service

-- ============================================================================
-- Verification Queries (for testing after migration)
-- ============================================================================

-- Verify tables created:
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public' AND table_name LIKE '%historical%' OR table_name LIKE '%coverage%';

-- Check indexes:
-- SELECT indexname, tablename FROM pg_indexes
-- WHERE tablename IN ('historical_bars', 'data_coverage', 'api_call_log');

-- Example insert (for testing):
-- INSERT INTO historical_bars (symbol, interval, timestamp, open, high, low, close, volume, data_source)
-- VALUES ('AAPL', '1d', '2025-01-29 00:00:00+00', 225.00, 227.50, 224.00, 226.75, 50000000, 'alpaca');

-- Query coverage after insert:
-- SELECT * FROM data_coverage WHERE symbol = 'AAPL';

-- ============================================================================
-- Storage Estimates
-- ============================================================================

-- One bar ~50 bytes (8 decimal fields × ~6 bytes avg)
-- AAPL 5m for 7 years: ~137,000 bars × 50 bytes = ~6.8MB
-- 20 symbols × 3 intervals = ~146MB total
-- Supabase free tier: 500MB (plenty of headroom)

-- ============================================================================
-- Maintenance Notes
-- ============================================================================

-- Cleanup old data (optional, if approaching storage limits):
-- DELETE FROM historical_bars
-- WHERE timestamp < NOW() - INTERVAL '2 years'
-- AND interval IN ('1m', '5m');  -- Keep daily data longer

-- Analyze table performance:
-- ANALYZE historical_bars;
-- VACUUM ANALYZE historical_bars;

-- Check storage usage:
-- SELECT
--   pg_size_pretty(pg_total_relation_size('historical_bars')) as total_size,
--   pg_size_pretty(pg_relation_size('historical_bars')) as table_size,
--   pg_size_pretty(pg_indexes_size('historical_bars')) as indexes_size;
