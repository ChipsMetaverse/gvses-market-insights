-- ============================================
-- Drawing Persistence Schema
-- Supabase PostgreSQL Migration
-- Version: 003
-- Date: 2025-11-27
-- ============================================

-- ============================================
-- Drawings Table
-- ============================================
CREATE TABLE IF NOT EXISTS drawings (
    -- Identity
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,

    -- Drawing Properties
    kind VARCHAR(20) NOT NULL CHECK (kind IN ('trendline', 'ray', 'horizontal')),
    name VARCHAR(255),
    visible BOOLEAN DEFAULT true,
    selected BOOLEAN DEFAULT false,

    -- Style Properties
    color VARCHAR(7) DEFAULT '#ffa500',
    width INTEGER DEFAULT 2 CHECK (width > 0 AND width <= 10),
    style VARCHAR(20) DEFAULT 'solid' CHECK (style IN ('solid', 'dashed', 'dotted')),

    -- Time/Price Coordinates (JSONB for flexibility)
    coordinates JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Indexes for Query Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_drawings_user_symbol
    ON drawings(user_id, symbol);

CREATE INDEX IF NOT EXISTS idx_drawings_user_created
    ON drawings(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_drawings_kind
    ON drawings(kind);

CREATE INDEX IF NOT EXISTS idx_drawings_symbol
    ON drawings(symbol);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================
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

-- ============================================
-- Trigger: Auto-update updated_at timestamp
-- ============================================
CREATE TRIGGER drawings_updated_at_trigger
    BEFORE UPDATE ON drawings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();  -- Reuse existing function from 001 migration

-- ============================================
-- Coordinate Validation Functions
-- ============================================

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

-- ============================================
-- Grants
-- ============================================

-- Users can read/write their own drawings
GRANT SELECT, INSERT, UPDATE, DELETE ON drawings TO authenticated;

-- Service role has full access
GRANT ALL ON drawings TO service_role;

-- Anonymous users cannot access drawings
REVOKE ALL ON drawings FROM anon;

-- ============================================
-- Comments
-- ============================================

COMMENT ON TABLE drawings IS 'User drawing annotations for trading charts (trendlines, rays, horizontal levels)';
COMMENT ON COLUMN drawings.coordinates IS 'JSONB containing time/price coordinate data, validated per drawing kind';
COMMENT ON COLUMN drawings.kind IS 'Drawing type: trendline (two points), ray (infinite line), horizontal (price level)';

-- ============================================
-- Migration Complete
-- ============================================

SELECT 'Drawing persistence schema created successfully!' AS status;
