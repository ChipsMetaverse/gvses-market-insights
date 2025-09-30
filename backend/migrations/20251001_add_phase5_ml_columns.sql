-- Phase 5 schema upgrade for ML-driven pattern confidence
-- Adds ML-related columns to pattern_events and introduces lifecycle history tracking

-- Ensure required extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Augment pattern_events with ML metadata columns
ALTER TABLE IF EXISTS pattern_events
    ADD COLUMN IF NOT EXISTS outcome_label TEXT,
    ADD COLUMN IF NOT EXISTS realized_pnl NUMERIC,
    ADD COLUMN IF NOT EXISTS max_drawdown NUMERIC,
    ADD COLUMN IF NOT EXISTS rule_confidence NUMERIC,
    ADD COLUMN IF NOT EXISTS ml_confidence NUMERIC,
    ADD COLUMN IF NOT EXISTS blended_confidence NUMERIC,
    ADD COLUMN IF NOT EXISTS prediction_latency_ms INTEGER,
    ADD COLUMN IF NOT EXISTS ml_features JSONB,
    ADD COLUMN IF NOT EXISTS ml_metadata JSONB,
    ADD COLUMN IF NOT EXISTS used_for_training BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS training_split TEXT,
    ADD COLUMN IF NOT EXISTS last_evaluated_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS evaluation_notes TEXT;

-- Indexes to optimise ML querying
CREATE INDEX IF NOT EXISTS idx_pattern_events_outcome_label ON pattern_events (outcome_label);
CREATE INDEX IF NOT EXISTS idx_pattern_events_training_split ON pattern_events (training_split);
CREATE INDEX IF NOT EXISTS idx_pattern_events_used_for_training ON pattern_events (used_for_training);
CREATE INDEX IF NOT EXISTS idx_pattern_events_last_evaluated ON pattern_events (last_evaluated_at);

-- Lifecycle history table to capture confidence trajectories
CREATE TABLE IF NOT EXISTS pattern_lifecycle_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID NOT NULL,
    previous_status TEXT,
    new_status TEXT,
    rule_confidence NUMERIC,
    ml_confidence NUMERIC,
    blended_confidence NUMERIC,
    reason TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_pattern_lifecycle_history_pattern
        FOREIGN KEY (pattern_id)
        REFERENCES pattern_events (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pattern_lifecycle_history_pattern ON pattern_lifecycle_history (pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_lifecycle_history_created_at ON pattern_lifecycle_history (created_at DESC);
