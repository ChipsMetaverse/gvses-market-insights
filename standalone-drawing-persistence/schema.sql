-- ============================================================================
-- Drawing Persistence Schema for GVSES Trading Platform
-- Standalone Test Version - Supabase PostgreSQL
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Main Drawings Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS drawings (
    -- Identity
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL, -- FK to auth.users
    symbol VARCHAR(20) NOT NULL, -- Stock symbol (TSLA, AAPL, etc.)

    -- Drawing Properties
    kind VARCHAR(20) NOT NULL CHECK (kind IN ('trendline', 'ray', 'horizontal')),
    name VARCHAR(255), -- Optional legend label
    visible BOOLEAN DEFAULT true,
    selected BOOLEAN DEFAULT false,

    -- Style Properties
    color VARCHAR(7) DEFAULT '#ffa500', -- Hex color
    width INTEGER DEFAULT 2 CHECK (width > 0 AND width <= 10), -- Line width in px
    style VARCHAR(20) DEFAULT 'solid' CHECK (style IN ('solid', 'dashed', 'dotted')),

    -- Time/Price Coordinates (JSON for flexibility)
    -- For trendline/ray: { a: { time: number, price: number }, b: { time: number, price: number } }
    -- For horizontal: { price: number, rotation?: number, t0?: number, t1?: number }
    coordinates JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Indexes for performance
    CONSTRAINT drawings_user_symbol_idx UNIQUE (id, user_id, symbol)
);

-- ============================================================================
-- Indexes for Query Performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_drawings_user_symbol
    ON drawings(user_id, symbol);

CREATE INDEX IF NOT EXISTS idx_drawings_user_created
    ON drawings(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_drawings_kind
    ON drawings(kind);

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================
ALTER TABLE drawings ENABLE ROW LEVEL SECURITY;

-- Users can only see their own drawings
CREATE POLICY drawings_select_policy ON drawings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own drawings
CREATE POLICY drawings_insert_policy ON drawings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own drawings
CREATE POLICY drawings_update_policy ON drawings
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can only delete their own drawings
CREATE POLICY drawings_delete_policy ON drawings
    FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- Trigger: Auto-update updated_at timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION update_drawings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER drawings_updated_at_trigger
    BEFORE UPDATE ON drawings
    FOR EACH ROW
    EXECUTE FUNCTION update_drawings_updated_at();

-- ============================================================================
-- Sample Data for Testing (Optional)
-- ============================================================================
-- Uncomment to insert test data:
-- INSERT INTO drawings (user_id, symbol, kind, coordinates) VALUES
--     ('00000000-0000-0000-0000-000000000000', 'TSLA', 'trendline',
--      '{"a": {"time": 1609459200, "price": 700}, "b": {"time": 1612137600, "price": 850}}'::jsonb),
--     ('00000000-0000-0000-0000-000000000000', 'TSLA', 'horizontal',
--      '{"price": 800, "rotation": 0}'::jsonb);

-- ============================================================================
-- Validation Functions
-- ============================================================================

-- Validate trendline/ray coordinates
CREATE OR REPLACE FUNCTION validate_trendline_coordinates(coords JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        coords ? 'a' AND coords ? 'b' AND
        coords->'a' ? 'time' AND coords->'a' ? 'price' AND
        coords->'b' ? 'time' AND coords->'b' ? 'price'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Validate horizontal coordinates
CREATE OR REPLACE FUNCTION validate_horizontal_coordinates(coords JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN coords ? 'price';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Add validation constraint
ALTER TABLE drawings ADD CONSTRAINT check_coordinates
    CHECK (
        (kind IN ('trendline', 'ray') AND validate_trendline_coordinates(coordinates)) OR
        (kind = 'horizontal' AND validate_horizontal_coordinates(coordinates))
    );

-- ============================================================================
-- Utility Views
-- ============================================================================

-- View: Recent drawings per symbol
CREATE OR REPLACE VIEW recent_drawings_by_symbol AS
SELECT
    symbol,
    kind,
    COUNT(*) as count,
    MAX(created_at) as last_created
FROM drawings
GROUP BY symbol, kind
ORDER BY last_created DESC;

-- View: Drawing statistics per user
CREATE OR REPLACE VIEW user_drawing_stats AS
SELECT
    user_id,
    COUNT(*) as total_drawings,
    COUNT(DISTINCT symbol) as symbols_with_drawings,
    MAX(created_at) as last_drawing_created
FROM drawings
GROUP BY user_id;

-- ============================================================================
-- Migration Complete
-- ============================================================================
-- To apply this schema to Supabase:
-- 1. Copy this SQL
-- 2. Go to Supabase Dashboard > SQL Editor
-- 3. Paste and run
-- 4. Verify tables created in Table Editor
