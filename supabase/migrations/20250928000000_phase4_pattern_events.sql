-- Phase 4: Pattern Events Table for Lifecycle Tracking
-- This migration creates the pattern_events table to track all pattern lifecycle transitions

-- Create pattern status enum
CREATE TYPE pattern_status AS ENUM (
    'pending',
    'confirmed', 
    'completed',
    'invalidated',
    'expired'
);

-- Create pattern_events table
CREATE TABLE IF NOT EXISTS pattern_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    status pattern_status NOT NULL DEFAULT 'pending',
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    target FLOAT,
    entry FLOAT,
    stoploss FLOAT,
    support FLOAT,
    resistance FLOAT,
    draw_commands JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    snapshot_url TEXT,
    operator_id TEXT,
    verdict TEXT CHECK (verdict IN ('bullish', 'bearish', 'neutral')),
    verdict_notes TEXT,
    rule_evaluation JSONB DEFAULT '{}'::jsonb,
    auto_generated BOOLEAN DEFAULT FALSE,
    parent_pattern_id UUID REFERENCES pattern_events(id)
);

-- Create indexes for performance
CREATE INDEX idx_pattern_events_symbol ON pattern_events(symbol);
CREATE INDEX idx_pattern_events_status ON pattern_events(status);
CREATE INDEX idx_pattern_events_created_at ON pattern_events(created_at DESC);
CREATE INDEX idx_pattern_events_symbol_timeframe ON pattern_events(symbol, timeframe);
CREATE INDEX idx_pattern_events_active ON pattern_events(status) 
    WHERE status IN ('pending', 'confirmed');

-- Create pattern lifecycle history table
CREATE TABLE IF NOT EXISTS pattern_lifecycle_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID NOT NULL REFERENCES pattern_events(id) ON DELETE CASCADE,
    old_status pattern_status,
    new_status pattern_status NOT NULL,
    transition_reason TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for lifecycle history
CREATE INDEX idx_lifecycle_history_pattern_id ON pattern_lifecycle_history(pattern_id);
CREATE INDEX idx_lifecycle_history_created_at ON pattern_lifecycle_history(created_at DESC);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_pattern_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    
    -- Set completed_at if transitioning to completed/invalidated/expired
    IF NEW.status IN ('completed', 'invalidated', 'expired') 
       AND OLD.status NOT IN ('completed', 'invalidated', 'expired') THEN
        NEW.completed_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER pattern_events_updated_at
    BEFORE UPDATE ON pattern_events
    FOR EACH ROW
    EXECUTE FUNCTION update_pattern_events_updated_at();

-- Function to log lifecycle transitions
CREATE OR REPLACE FUNCTION log_pattern_lifecycle_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if status actually changed
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO pattern_lifecycle_history (
            pattern_id,
            old_status,
            new_status,
            transition_reason,
            metadata
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            COALESCE(NEW.rule_evaluation->>'reason', 'manual'),
            jsonb_build_object(
                'confidence', NEW.confidence,
                'old_confidence', OLD.confidence,
                'auto_generated', NEW.auto_generated,
                'verdict', NEW.verdict
            )
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for lifecycle logging
CREATE TRIGGER pattern_lifecycle_transition
    AFTER UPDATE ON pattern_events
    FOR EACH ROW
    EXECUTE FUNCTION log_pattern_lifecycle_transition();

-- Function to get active patterns for a symbol
CREATE OR REPLACE FUNCTION get_active_patterns(
    p_symbol TEXT,
    p_timeframe TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    pattern_type TEXT,
    status pattern_status,
    confidence FLOAT,
    target FLOAT,
    created_at TIMESTAMPTZ,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.id,
        pe.pattern_type,
        pe.status,
        pe.confidence,
        pe.target,
        pe.created_at,
        pe.metadata
    FROM pattern_events pe
    WHERE pe.symbol = p_symbol
        AND pe.status IN ('pending', 'confirmed')
        AND (p_timeframe IS NULL OR pe.timeframe = p_timeframe)
    ORDER BY pe.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to expire old patterns
CREATE OR REPLACE FUNCTION expire_old_patterns(
    p_max_age_hours INTEGER DEFAULT 72
)
RETURNS INTEGER AS $$
DECLARE
    v_expired_count INTEGER;
BEGIN
    UPDATE pattern_events
    SET status = 'expired',
        rule_evaluation = jsonb_build_object(
            'reason', 'expired_by_time',
            'max_age_hours', p_max_age_hours,
            'expired_at', NOW()
        )
    WHERE status IN ('pending', 'confirmed')
        AND created_at < NOW() - INTERVAL '1 hour' * p_max_age_hours;
    
    GET DIAGNOSTICS v_expired_count = ROW_COUNT;
    RETURN v_expired_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get pattern success rate statistics
CREATE OR REPLACE FUNCTION get_pattern_success_stats(
    p_pattern_type TEXT DEFAULT NULL,
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    pattern_type TEXT,
    total_patterns BIGINT,
    completed_count BIGINT,
    invalidated_count BIGINT,
    expired_count BIGINT,
    success_rate FLOAT,
    avg_confidence FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.pattern_type,
        COUNT(*) as total_patterns,
        COUNT(*) FILTER (WHERE pe.status = 'completed') as completed_count,
        COUNT(*) FILTER (WHERE pe.status = 'invalidated') as invalidated_count,
        COUNT(*) FILTER (WHERE pe.status = 'expired') as expired_count,
        ROUND(
            COUNT(*) FILTER (WHERE pe.status = 'completed')::NUMERIC / 
            NULLIF(COUNT(*) FILTER (WHERE pe.status IN ('completed', 'invalidated')), 0) * 100,
            2
        ) as success_rate,
        ROUND(AVG(pe.confidence)::NUMERIC, 3) as avg_confidence
    FROM pattern_events pe
    WHERE pe.created_at >= NOW() - INTERVAL '1 day' * p_days
        AND (p_pattern_type IS NULL OR pe.pattern_type = p_pattern_type)
    GROUP BY pe.pattern_type
    ORDER BY total_patterns DESC;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE pattern_events IS 'Tracks all pattern lifecycle events and transitions for Phase 4 pattern logic';
COMMENT ON TABLE pattern_lifecycle_history IS 'Audit log of all pattern status transitions';
COMMENT ON FUNCTION get_active_patterns IS 'Returns active patterns (pending or confirmed) for a given symbol';
COMMENT ON FUNCTION expire_old_patterns IS 'Batch expire patterns older than specified hours';
COMMENT ON FUNCTION get_pattern_success_stats IS 'Calculate pattern success rate statistics';