-- =====================================================
-- Behavioral Coaching Platform - Phase 1 Schema
-- Progressive Behavioral Architecture
-- =====================================================
--
-- This migration implements the foundation for non-directive
-- trading psychology coaching based on ACT (Acceptance and
-- Commitment Therapy) principles and behavioral analytics.
--
-- Regulatory Positioning: Educational wellness tool
-- NOT investment advice, NOT medical device
--
-- Phase 1 Components:
-- 1. Trade Journal (Reflection Engine)
-- 2. Emotional Analytics
-- 3. ACT Exercise Library
-- 4. Behavioral Pattern Detection
-- =====================================================

-- =====================================================
-- 1. TRADE JOURNAL (Core Reflection Engine)
-- =====================================================
-- Captures trade execution data with emotional context
-- for post-trade reflection and pattern analysis

CREATE TABLE IF NOT EXISTS trade_journal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Trade Execution Data
    symbol TEXT NOT NULL,
    entry_price NUMERIC(12, 4) NOT NULL,
    exit_price NUMERIC(12, 4),
    entry_timestamp TIMESTAMPTZ NOT NULL,
    exit_timestamp TIMESTAMPTZ,
    position_size INTEGER NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('long', 'short')),
    pl NUMERIC(12, 2), -- Profit/Loss in currency
    pl_percent NUMERIC(8, 4), -- P/L as percentage

    -- Market Context (for pattern analysis)
    timeframe TEXT NOT NULL,
    chart_snapshot_url TEXT, -- Screenshot from TradingView
    market_conditions JSONB, -- BTD, PDH/PDL, technical levels

    -- Psychological Data (user-supplied)
    emotional_tags TEXT[], -- ['fomo', 'revenge', 'disciplined', 'anxious']
    plan_entry TEXT, -- "What was my plan for this trade?"
    plan_exit TEXT, -- "What was my exit strategy?"
    actual_vs_plan TEXT, -- "Did I follow the plan? Why/why not?"
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),

    -- Voice Memo Integration (ElevenLabs)
    voice_plan_url TEXT, -- Pre-trade voice recording
    voice_review_url TEXT, -- Post-trade reflection

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Behavioral Classification (computed)
    is_disciplined BOOLEAN, -- Followed plan?
    is_impulsive BOOLEAN, -- Opened within 5min of stop-out?
    is_fomo BOOLEAN, -- Entered after rapid price movement?
    is_revenge BOOLEAN, -- Opened within 10min of loss?

    CONSTRAINT valid_emotional_tags CHECK (
        emotional_tags <@ ARRAY[
            'disciplined', 'anxious', 'confident', 'fearful',
            'greedy', 'fomo', 'revenge', 'patient', 'impulsive',
            'calm', 'stressed', 'frustrated', 'excited'
        ]
    )
);

-- Indexes for performance
CREATE INDEX idx_trade_journal_user_timestamp ON trade_journal(user_id, entry_timestamp DESC);
CREATE INDEX idx_trade_journal_symbol ON trade_journal(symbol);
CREATE INDEX idx_trade_journal_emotional_tags ON trade_journal USING GIN(emotional_tags);
CREATE INDEX idx_trade_journal_behavioral ON trade_journal(user_id, is_disciplined, is_impulsive, is_fomo, is_revenge);

-- Row Level Security
ALTER TABLE trade_journal ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own trades"
    ON trade_journal FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own trades"
    ON trade_journal FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own trades"
    ON trade_journal FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own trades"
    ON trade_journal FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- 2. WEEKLY BEHAVIORAL INSIGHTS
-- =====================================================
-- Pre-computed analytics for user dashboard
-- Compares disciplined vs impulsive trading performance

CREATE TABLE IF NOT EXISTS weekly_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Time Period
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,

    -- Trading Volume
    total_trades INTEGER NOT NULL DEFAULT 0,
    disciplined_trades INTEGER NOT NULL DEFAULT 0,
    impulsive_trades INTEGER NOT NULL DEFAULT 0,
    fomo_trades INTEGER NOT NULL DEFAULT 0,
    revenge_trades INTEGER NOT NULL DEFAULT 0,

    -- Performance Metrics
    disciplined_win_rate NUMERIC(5, 2), -- e.g., 67.00%
    impulsive_win_rate NUMERIC(5, 2),
    disciplined_avg_pl NUMERIC(12, 2),
    impulsive_avg_pl NUMERIC(12, 2),

    -- Emotional Costs
    cost_of_fomo NUMERIC(12, 2), -- Total $ lost to FOMO trades
    cost_of_revenge NUMERIC(12, 2), -- Total $ lost to revenge trades
    cost_of_emotions NUMERIC(12, 2), -- Total emotional trading cost

    -- Behavioral Trends
    best_trading_hours JSONB, -- {'10am-12pm': {trades: 15, winRate: 0.73}}
    worst_emotional_states JSONB, -- {'anxious': -$500, 'revenge': -$800}

    -- ACT Engagement
    act_exercises_completed INTEGER DEFAULT 0,
    act_exercises_triggered INTEGER DEFAULT 0,
    act_completion_rate NUMERIC(5, 2),

    -- Metadata
    generated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_user_week UNIQUE(user_id, week_start)
);

-- Indexes
CREATE INDEX idx_weekly_insights_user ON weekly_insights(user_id, week_start DESC);

-- RLS
ALTER TABLE weekly_insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own insights"
    ON weekly_insights FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert insights"
    ON weekly_insights FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- =====================================================
-- 3. ACT EXERCISE LIBRARY
-- =====================================================
-- Content repository for ACT-based psychological exercises
-- Educational wellness content (NOT medical treatment)

CREATE TABLE IF NOT EXISTS act_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Exercise Metadata
    type TEXT NOT NULL, -- 'cognitive_defusion', 'values_clarification', 'mindfulness'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),

    -- Content
    instructions JSONB NOT NULL, -- Step-by-step exercise instructions
    audio_url TEXT, -- Optional guided audio
    visual_assets JSONB, -- Images, animations for exercise

    -- Trigger Conditions (when to suggest this exercise)
    trigger_contexts TEXT[], -- ['post_stopout', 'pre_fomo_entry', 'high_stress']

    -- Educational Category
    skill_taught TEXT NOT NULL, -- 'emotion_regulation', 'cognitive_flexibility', etc
    clinical_basis TEXT NOT NULL, -- Research foundation (Hayes et al., 2006)

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,

    CONSTRAINT valid_exercise_types CHECK (
        type IN (
            'cognitive_defusion',      -- "Silly Voice" technique
            'values_clarification',     -- "What kind of trader do I want to be?"
            'mindfulness',              -- "Leaves on Stream"
            'acceptance',               -- "Passengers on Bus"
            'committed_action',         -- Action planning
            'present_moment'            -- Mindful breathing
        )
    )
);

-- Indexes
CREATE INDEX idx_act_exercises_type ON act_exercises(type);
CREATE INDEX idx_act_exercises_triggers ON act_exercises USING GIN(trigger_contexts);

-- RLS (public read for all authenticated users)
ALTER TABLE act_exercises ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view exercises"
    ON act_exercises FOR SELECT
    USING (auth.role() = 'authenticated');

-- =====================================================
-- 4. ACT EXERCISE COMPLETIONS (User Progress Tracking)
-- =====================================================

CREATE TABLE IF NOT EXISTS act_exercise_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    exercise_id UUID REFERENCES act_exercises(id) ON DELETE CASCADE NOT NULL,

    -- Context
    trigger_context TEXT NOT NULL, -- 'post_stopout', 'pre_fomo_entry', etc
    related_trade_id UUID REFERENCES trade_journal(id), -- Link to specific trade

    -- Completion Data
    completed BOOLEAN NOT NULL DEFAULT false,
    duration_seconds INTEGER,
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    user_notes TEXT,

    -- Effectiveness (measured by behavior change)
    prevented_impulsive_trade BOOLEAN,
    improved_emotional_state BOOLEAN,

    -- Metadata
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_trigger_contexts CHECK (
        trigger_context IN (
            'post_stopout',
            'pre_fomo_entry',
            'after_loss_streak',
            'high_stress_detected',
            'plan_deviation',
            'revenge_trading_risk',
            'user_requested'
        )
    )
);

-- Indexes
CREATE INDEX idx_act_completions_user ON act_exercise_completions(user_id, started_at DESC);
CREATE INDEX idx_act_completions_exercise ON act_exercise_completions(exercise_id);
CREATE INDEX idx_act_completions_context ON act_exercise_completions(trigger_context);

-- RLS
ALTER TABLE act_exercise_completions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own completions"
    ON act_exercise_completions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own completions"
    ON act_exercise_completions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own completions"
    ON act_exercise_completions FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- 5. BEHAVIORAL PATTERNS (AI Detection Results)
-- =====================================================
-- Stores detected behavioral patterns for user awareness
-- Educational insights, NOT investment advice

CREATE TABLE IF NOT EXISTS behavioral_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,

    -- Pattern Classification
    pattern_type TEXT NOT NULL,
    confidence NUMERIC(3, 2) CHECK (confidence BETWEEN 0 AND 1),
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),

    -- Evidence
    supporting_trades UUID[] NOT NULL, -- Array of trade_journal IDs
    sample_size INTEGER NOT NULL, -- How many trades analyzed

    -- Insight (Educational Content)
    title TEXT NOT NULL, -- "Possible revenge trading pattern detected"
    description TEXT NOT NULL, -- "You lose money 8/10 times when trading within 5min of stop-out"
    suggestion TEXT NOT NULL, -- "Consider implementing a 10-minute cooling-off period"

    -- Statistical Backing
    pattern_metrics JSONB NOT NULL, -- {win_rate: 0.20, avg_loss: -$150, frequency: 8}

    -- Status
    acknowledged BOOLEAN DEFAULT false,
    dismissed BOOLEAN DEFAULT false,
    user_feedback TEXT,

    -- Metadata
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,

    CONSTRAINT valid_pattern_types CHECK (
        pattern_type IN (
            'revenge_trading',
            'fomo_entries',
            'overtrading',
            'plan_deviation',
            'loss_chasing',
            'profit_cutting',
            'stop_moving',
            'time_of_day_bias',
            'emotional_state_correlation'
        )
    )
);

-- Indexes
CREATE INDEX idx_behavioral_patterns_user ON behavioral_patterns(user_id, detected_at DESC);
CREATE INDEX idx_behavioral_patterns_type ON behavioral_patterns(pattern_type);
CREATE INDEX idx_behavioral_patterns_unacknowledged ON behavioral_patterns(user_id, acknowledged) WHERE acknowledged = false;

-- RLS
ALTER TABLE behavioral_patterns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own patterns"
    ON behavioral_patterns FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own patterns"
    ON behavioral_patterns FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- 6. USER BEHAVIORAL SETTINGS
-- =====================================================
-- User preferences for coaching features (opt-in philosophy)

CREATE TABLE IF NOT EXISTS user_behavioral_settings (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Master Switches
    coaching_enabled BOOLEAN DEFAULT true,
    journal_enabled BOOLEAN DEFAULT true,
    insights_enabled BOOLEAN DEFAULT true,
    act_exercises_enabled BOOLEAN DEFAULT true,
    pattern_detection_enabled BOOLEAN DEFAULT true,

    -- Journal Auto-Capture
    auto_capture_enabled BOOLEAN DEFAULT true,
    require_emotional_tags BOOLEAN DEFAULT false,
    require_plan_entry BOOLEAN DEFAULT false,
    require_voice_memo BOOLEAN DEFAULT false,

    -- ACT Exercise Preferences
    act_trigger_frequency TEXT DEFAULT 'moderate' CHECK (
        act_trigger_frequency IN ('minimal', 'moderate', 'aggressive')
    ),
    preferred_exercise_types TEXT[], -- User can disable certain types

    -- Notification Preferences
    weekly_insights_email BOOLEAN DEFAULT true,
    pattern_alert_push BOOLEAN DEFAULT true,

    -- Privacy Settings
    share_anonymous_data BOOLEAN DEFAULT false, -- For platform improvement

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE user_behavioral_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own settings"
    ON user_behavioral_settings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings"
    ON user_behavioral_settings FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings"
    ON user_behavioral_settings FOR UPDATE
    USING (auth.uid() = user_id);

-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Function to auto-compute behavioral flags on trade insert/update
CREATE OR REPLACE FUNCTION compute_behavioral_flags()
RETURNS TRIGGER AS $$
DECLARE
    recent_loss RECORD;
    price_movement NUMERIC;
BEGIN
    -- Check for revenge trading (opened within 10min of loss)
    SELECT * INTO recent_loss
    FROM trade_journal
    WHERE user_id = NEW.user_id
      AND pl < 0
      AND exit_timestamp IS NOT NULL
      AND exit_timestamp > NEW.entry_timestamp - INTERVAL '10 minutes'
      AND exit_timestamp < NEW.entry_timestamp
    ORDER BY exit_timestamp DESC
    LIMIT 1;

    IF FOUND THEN
        NEW.is_revenge := true;
        NEW.is_impulsive := true;
    ELSE
        NEW.is_revenge := false;
    END IF;

    -- Check for disciplined (has plan_entry and plan_exit)
    IF NEW.plan_entry IS NOT NULL AND NEW.plan_exit IS NOT NULL THEN
        NEW.is_disciplined := true;
    ELSE
        NEW.is_disciplined := false;
    END IF;

    -- Check for impulsive (opened <5min after previous trade)
    IF EXISTS (
        SELECT 1 FROM trade_journal
        WHERE user_id = NEW.user_id
          AND entry_timestamp > NEW.entry_timestamp - INTERVAL '5 minutes'
          AND entry_timestamp < NEW.entry_timestamp
          AND id != NEW.id
    ) THEN
        NEW.is_impulsive := true;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-compute flags
CREATE TRIGGER compute_behavioral_flags_trigger
    BEFORE INSERT OR UPDATE ON trade_journal
    FOR EACH ROW
    EXECUTE FUNCTION compute_behavioral_flags();

-- Function to update weekly insights (called by backend cron job)
CREATE OR REPLACE FUNCTION update_weekly_insights(target_user_id UUID, target_week_start DATE)
RETURNS void AS $$
DECLARE
    week_end_date DATE := target_week_start + INTERVAL '6 days';
    total_count INTEGER;
    disciplined_count INTEGER;
    impulsive_count INTEGER;
    fomo_count INTEGER;
    revenge_count INTEGER;
    disciplined_wins NUMERIC;
    impulsive_wins NUMERIC;
    disciplined_pl NUMERIC;
    impulsive_pl NUMERIC;
    fomo_cost NUMERIC;
    revenge_cost NUMERIC;
    act_completed INTEGER;
    act_triggered INTEGER;
BEGIN
    -- Count trades
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE is_disciplined = true),
        COUNT(*) FILTER (WHERE is_impulsive = true),
        COUNT(*) FILTER (WHERE is_fomo = true),
        COUNT(*) FILTER (WHERE is_revenge = true)
    INTO
        total_count, disciplined_count, impulsive_count, fomo_count, revenge_count
    FROM trade_journal
    WHERE user_id = target_user_id
      AND entry_timestamp >= target_week_start
      AND entry_timestamp < week_end_date + INTERVAL '1 day'
      AND exit_timestamp IS NOT NULL;

    -- Calculate win rates
    SELECT
        (COUNT(*) FILTER (WHERE pl > 0)::NUMERIC / NULLIF(COUNT(*) FILTER (WHERE is_disciplined = true), 0)) * 100,
        (COUNT(*) FILTER (WHERE pl > 0 AND is_impulsive = true)::NUMERIC / NULLIF(COUNT(*) FILTER (WHERE is_impulsive = true), 0)) * 100
    INTO disciplined_wins, impulsive_wins
    FROM trade_journal
    WHERE user_id = target_user_id
      AND entry_timestamp >= target_week_start
      AND entry_timestamp < week_end_date + INTERVAL '1 day'
      AND exit_timestamp IS NOT NULL;

    -- Calculate average P/L
    SELECT
        AVG(pl) FILTER (WHERE is_disciplined = true),
        AVG(pl) FILTER (WHERE is_impulsive = true)
    INTO disciplined_pl, impulsive_pl
    FROM trade_journal
    WHERE user_id = target_user_id
      AND entry_timestamp >= target_week_start
      AND entry_timestamp < week_end_date + INTERVAL '1 day'
      AND exit_timestamp IS NOT NULL;

    -- Calculate emotional costs
    SELECT
        COALESCE(SUM(pl) FILTER (WHERE is_fomo = true AND pl < 0), 0),
        COALESCE(SUM(pl) FILTER (WHERE is_revenge = true AND pl < 0), 0)
    INTO fomo_cost, revenge_cost
    FROM trade_journal
    WHERE user_id = target_user_id
      AND entry_timestamp >= target_week_start
      AND entry_timestamp < week_end_date + INTERVAL '1 day'
      AND exit_timestamp IS NOT NULL;

    -- ACT exercise stats
    SELECT
        COUNT(*) FILTER (WHERE completed = true),
        COUNT(*)
    INTO act_completed, act_triggered
    FROM act_exercise_completions
    WHERE user_id = target_user_id
      AND started_at >= target_week_start
      AND started_at < week_end_date + INTERVAL '1 day';

    -- Insert or update weekly insights
    INSERT INTO weekly_insights (
        user_id, week_start, week_end,
        total_trades, disciplined_trades, impulsive_trades, fomo_trades, revenge_trades,
        disciplined_win_rate, impulsive_win_rate,
        disciplined_avg_pl, impulsive_avg_pl,
        cost_of_fomo, cost_of_revenge, cost_of_emotions,
        act_exercises_completed, act_exercises_triggered,
        act_completion_rate
    ) VALUES (
        target_user_id, target_week_start, week_end_date,
        total_count, disciplined_count, impulsive_count, fomo_count, revenge_count,
        ROUND(disciplined_wins, 2), ROUND(impulsive_wins, 2),
        ROUND(disciplined_pl, 2), ROUND(impulsive_pl, 2),
        ROUND(fomo_cost, 2), ROUND(revenge_cost, 2), ROUND(fomo_cost + revenge_cost, 2),
        act_completed, act_triggered,
        CASE WHEN act_triggered > 0 THEN ROUND((act_completed::NUMERIC / act_triggered) * 100, 2) ELSE 0 END
    )
    ON CONFLICT (user_id, week_start)
    DO UPDATE SET
        total_trades = EXCLUDED.total_trades,
        disciplined_trades = EXCLUDED.disciplined_trades,
        impulsive_trades = EXCLUDED.impulsive_trades,
        disciplined_win_rate = EXCLUDED.disciplined_win_rate,
        impulsive_win_rate = EXCLUDED.impulsive_win_rate,
        cost_of_emotions = EXCLUDED.cost_of_emotions,
        generated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. SEED DATA - ACT Exercise Library
-- =====================================================
-- Pre-populated ACT exercises for immediate use

INSERT INTO act_exercises (type, title, description, duration_seconds, difficulty, instructions, trigger_contexts, skill_taught, clinical_basis) VALUES
(
    'cognitive_defusion',
    'The Silly Voice Technique',
    'Reduce the power of distressing thoughts by repeating them in a cartoon voice.',
    120,
    'beginner',
    '{
        "steps": [
            "Identify your most distressing trading thought (e.g., \"I''m a terrible trader\")",
            "Close your eyes and repeat it in your normal voice 3 times",
            "Now repeat it in a Mickey Mouse or robot voice 3 times",
            "Notice how the emotional charge decreases when the voice changes",
            "This is defusion - separating you from the thought"
        ],
        "key_insight": "Thoughts are just words, not absolute truths"
    }'::jsonb,
    ARRAY['post_stopout', 'after_loss_streak', 'high_stress_detected'],
    'emotion_regulation',
    'Hayes et al. (2006) - Acceptance and Commitment Therapy'
),
(
    'mindfulness',
    'Leaves on a Stream',
    'Practice non-attachment to market fluctuations by visualizing thoughts floating away.',
    180,
    'beginner',
    '{
        "steps": [
            "Close your eyes and imagine sitting by a gentle stream",
            "Watch leaves floating on the water, carried by the current",
            "As thoughts arise (about trades, losses, profits), place each on a leaf",
            "Watch the leaf float downstream and out of sight",
            "Don''t judge the thought - just observe it passing",
            "Return to watching the stream when your mind wanders"
        ],
        "key_insight": "You can observe thoughts without being controlled by them"
    }'::jsonb,
    ARRAY['pre_fomo_entry', 'plan_deviation', 'user_requested'],
    'present_moment',
    'Kabat-Zinn (1990) - Mindfulness-Based Stress Reduction'
),
(
    'acceptance',
    'Passengers on the Bus',
    'Learn to drive toward your goals while anxious thoughts are present.',
    240,
    'intermediate',
    '{
        "steps": [
            "Imagine you''re driving a bus toward your trading destination (long-term success)",
            "Distressing thoughts are rowdy passengers: \"You''re a loser\", \"Take profit now\", \"Revenge trade!\"",
            "The passengers can be loud, but YOU are the driver",
            "You don''t have to kick them off the bus - just keep driving",
            "Acknowledge the passengers (\"I hear you\") but stay on your route",
            "Your values (discipline, patience) are your GPS, not the passengers'' demands"
        ],
        "key_insight": "You can have anxiety and still take committed action"
    }'::jsonb,
    ARRAY['revenge_trading_risk', 'high_stress_detected', 'plan_deviation'],
    'committed_action',
    'Harris (2009) - ACT Made Simple'
),
(
    'values_clarification',
    'Future-You Trading Compass',
    'Clarify what kind of trader you want to become to guide present decisions.',
    300,
    'intermediate',
    '{
        "steps": [
            "Close your eyes and imagine yourself 5 years from now as a successful trader",
            "What qualities does Future-You embody? (Patient? Disciplined? Calm?)",
            "How does Future-You handle losses? (Learns from them? Stays detached?)",
            "What did Present-You do to become Future-You? (Followed plans? Journaled?)",
            "When facing a decision today, ask: \"What would Future-You do?\"",
            "Commit to one action today that aligns with Future-You''s values"
        ],
        "key_insight": "Values provide direction when emotions pull you off course"
    }'::jsonb,
    ARRAY['user_requested', 'after_loss_streak'],
    'values_clarification',
    'Hayes et al. (2012) - Process-Based CBT'
),
(
    'present_moment',
    'Box Breathing for Trade Stress',
    'Use rhythmic breathing to calm the nervous system before high-stakes decisions.',
    240,
    'beginner',
    '{
        "steps": [
            "Sit comfortably with feet flat on the floor",
            "Inhale slowly through your nose for 4 counts (visualize tracing one side of a box)",
            "Hold your breath for 4 counts (trace the top of the box)",
            "Exhale slowly through your mouth for 4 counts (trace the third side)",
            "Hold empty lungs for 4 counts (complete the box)",
            "Repeat for 4 complete cycles (4 boxes)",
            "Notice the calm that emerges from the rhythm"
        ],
        "key_insight": "Controlling breath controls stress response"
    }'::jsonb,
    ARRAY['pre_fomo_entry', 'high_stress_detected', 'revenge_trading_risk'],
    'emotion_regulation',
    'U.S. Navy SEALs - Combat Stress Management Protocol'
);

-- =====================================================
-- 9. COMPLIANCE & LEGAL DISCLAIMERS
-- =====================================================
-- Stored in database for consistent display across platform

CREATE TABLE IF NOT EXISTS legal_disclaimers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    effective_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_disclaimer_types CHECK (
        type IN (
            'wellness_education',
            'not_investment_advice',
            'not_medical_device',
            'user_responsibility',
            'data_privacy'
        )
    )
);

INSERT INTO legal_disclaimers (type, title, content, effective_date) VALUES
(
    'wellness_education',
    'Wellness Education Disclaimer',
    'The behavioral coaching features provided by this platform are for educational and wellness purposes only. They are designed to help you develop self-awareness and psychological flexibility in trading contexts. These features do NOT constitute medical advice, mental health treatment, diagnosis, or therapy. If you are experiencing significant emotional distress, anxiety, depression, or other mental health concerns, please consult a licensed mental health professional.',
    CURRENT_DATE
),
(
    'not_investment_advice',
    'Not Investment Advice',
    'The insights, patterns, and suggestions provided by our behavioral analysis system are educational in nature and do NOT constitute investment advice, recommendations to buy or sell securities, or personalized financial guidance. All trading decisions are your sole responsibility. The platform analyzes your historical behavior to help you recognize patterns, but does not tell you what trades to make. Past performance does not guarantee future results.',
    CURRENT_DATE
),
(
    'not_medical_device',
    'Not a Medical Device',
    'Any biofeedback features (if enabled) are wellness tools designed for general stress management and self-awareness. They are NOT medical devices and are not intended to diagnose, treat, cure, or prevent any disease or medical condition. Heart rate variability (HRV) data is provided for educational purposes only. Consult a physician before using biofeedback if you have any cardiac conditions.',
    CURRENT_DATE
),
(
    'user_responsibility',
    'User Responsibility',
    'You acknowledge that trading involves substantial risk of loss and is not suitable for all investors. The psychological coaching tools provided may help you develop better trading discipline, but they cannot eliminate market risk or guarantee profitable outcomes. You are solely responsible for your trading decisions, risk management, and compliance with all applicable laws and regulations.',
    CURRENT_DATE
);

-- RLS for disclaimers (public read)
ALTER TABLE legal_disclaimers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view disclaimers"
    ON legal_disclaimers FOR SELECT
    USING (true);

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
--
-- Next Steps:
-- 1. Run this migration: psql -f 006_behavioral_coaching_phase1.sql
-- 2. Verify tables created: \dt in psql
-- 3. Test RLS policies with test users
-- 4. Implement backend API endpoints (mcp_server.py)
-- 5. Build frontend components (React/TypeScript)
--
-- Regulatory Notes:
-- - All disclaimers must be displayed prominently in UI
-- - ACT exercises positioned as "wellness education"
-- - Pattern detection shows insights, NOT advice
-- - Users retain full trading autonomy
-- =====================================================
