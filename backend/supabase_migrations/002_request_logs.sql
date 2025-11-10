-- ============================================
-- Request Logging Schema
-- Supabase PostgreSQL Migration
-- Version: 1.1
-- Date: 2025-11-09
-- ============================================

-- Ensure UUID extension is available (no-op if already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Request Logs Table
-- ============================================

CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event TEXT NOT NULL,
    request_id TEXT,
    path TEXT,
    method TEXT,
    client_ip TEXT,
    forwarded_for TEXT,
    user_agent TEXT,
    session_id TEXT,
    user_id TEXT,
    duration_ms NUMERIC(12, 3),
    cost_summary JSONB,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Helpful indexes for querying request history
CREATE INDEX IF NOT EXISTS idx_request_logs_created_at
    ON request_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_request_logs_event
    ON request_logs (event);

CREATE INDEX IF NOT EXISTS idx_request_logs_request_id
    ON request_logs (request_id)
    WHERE request_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_request_logs_user_id
    ON request_logs (user_id)
    WHERE user_id IS NOT NULL;
