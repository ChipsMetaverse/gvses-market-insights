-- ============================================
-- Market News Storage Schema
-- Supabase PostgreSQL Migration
-- Version: 1.0
-- Date: 2025-12-16
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- ============================================
-- Market News Table
-- ============================================

CREATE TABLE IF NOT EXISTS market_news (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10),
    headline TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    source VARCHAR(50) NOT NULL DEFAULT 'unknown',
    source_url TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    sentiment_score DECIMAL(5, 2),
    relevance_score DECIMAL(5, 2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Indexes for Performance
-- ============================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_market_news_symbol
    ON market_news (symbol) WHERE symbol IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_market_news_published_at
    ON market_news (published_at DESC);

-- Composite index for symbol + published_at queries (most common pattern)
CREATE INDEX IF NOT EXISTS idx_market_news_symbol_published
    ON market_news (symbol, published_at DESC) WHERE symbol IS NOT NULL;

-- Source tracking
CREATE INDEX IF NOT EXISTS idx_market_news_source
    ON market_news (source);

-- Sentiment analysis queries
CREATE INDEX IF NOT EXISTS idx_market_news_sentiment
    ON market_news (sentiment_score) WHERE sentiment_score IS NOT NULL;

-- Full-text search on headlines
CREATE INDEX IF NOT EXISTS idx_market_news_headline_trgm
    ON market_news USING gin (headline gin_trgm_ops);

-- JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_market_news_metadata_gin
    ON market_news USING gin (metadata);

-- ============================================
-- Triggers and Functions
-- ============================================

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_market_news_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_market_news_timestamp
    BEFORE UPDATE ON market_news
    FOR EACH ROW
    EXECUTE FUNCTION update_market_news_timestamp();

-- ============================================
-- Cleanup Function
-- ============================================

-- Function to clean up old news (keep last 6 months)
CREATE OR REPLACE FUNCTION cleanup_old_market_news()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM market_news
    WHERE published_at < NOW() - INTERVAL '6 months';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Row Level Security (RLS)
-- ============================================

ALTER TABLE market_news ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Public read access" ON market_news
    FOR SELECT USING (true);

-- Only service role can write/update/delete
CREATE POLICY "Service role write" ON market_news
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- Permissions
-- ============================================

GRANT SELECT ON market_news TO anon, authenticated;
GRANT ALL ON market_news TO service_role;

-- ============================================
-- Helpful Views
-- ============================================

-- Recent news summary view
CREATE OR REPLACE VIEW recent_market_news AS
SELECT
    symbol,
    headline,
    source,
    published_at,
    sentiment_score,
    source_url
FROM market_news
WHERE published_at >= NOW() - INTERVAL '7 days'
ORDER BY published_at DESC;

GRANT SELECT ON recent_market_news TO anon, authenticated;

-- News by symbol view
CREATE OR REPLACE VIEW news_by_symbol AS
SELECT
    symbol,
    COUNT(*) as article_count,
    AVG(sentiment_score) as avg_sentiment,
    MAX(published_at) as latest_article,
    MIN(published_at) as earliest_article
FROM market_news
WHERE symbol IS NOT NULL
GROUP BY symbol
ORDER BY article_count DESC;

GRANT SELECT ON news_by_symbol TO anon, authenticated;

-- ============================================
-- Comments
-- ============================================

COMMENT ON TABLE market_news IS 'Cached market news articles from various sources (Yahoo Finance, CNBC, etc.)';
COMMENT ON COLUMN market_news.symbol IS 'Stock ticker symbol (nullable for general market news)';
COMMENT ON COLUMN market_news.headline IS 'Article headline/title';
COMMENT ON COLUMN market_news.content IS 'Full article content or description';
COMMENT ON COLUMN market_news.summary IS 'Brief summary of the article';
COMMENT ON COLUMN market_news.source IS 'News source (yahoo, cnbc, etc.)';
COMMENT ON COLUMN market_news.source_url IS 'Original article URL';
COMMENT ON COLUMN market_news.published_at IS 'Article publication timestamp';
COMMENT ON COLUMN market_news.sentiment_score IS 'Sentiment analysis score (-100 to 100)';
COMMENT ON COLUMN market_news.relevance_score IS 'Relevance score for the symbol (0-100)';
COMMENT ON COLUMN market_news.metadata IS 'Additional article metadata (author, tags, etc.)';

-- ============================================
-- Initial Statistics
-- ============================================

ANALYZE market_news;

SELECT 'Market news table created successfully!' AS status;
