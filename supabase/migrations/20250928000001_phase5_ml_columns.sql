-- Phase 5: ML-Driven Pattern Confidence - Schema Extensions
-- This migration adds ML training and inference columns to support machine learning features

-- Add ML-specific columns to pattern_events table
ALTER TABLE pattern_events ADD COLUMN IF NOT EXISTS
-- Training labels and outcomes
outcome_label VARCHAR CHECK (outcome_label IN ('positive', 'negative', 'neutral')),
realized_pnl FLOAT,                           -- Actual profit/loss when pattern completed
max_favorable_move FLOAT,                     -- Peak favorable price movement
max_adverse_move FLOAT,                       -- Peak adverse price movement (drawdown)
days_to_completion INTEGER,                   -- Time to reach target/invalidation
target_accuracy FLOAT,                        -- How close final price was to predicted target

-- ML model predictions and metadata
ml_confidence FLOAT CHECK (ml_confidence >= 0 AND ml_confidence <= 1),
ml_model_version VARCHAR,                     -- Model version that generated prediction
ml_features JSONB DEFAULT '{}'::jsonb,       -- Feature vector used for prediction
ml_prediction_metadata JSONB DEFAULT '{}'::jsonb, -- Model outputs, probabilities, etc.
predicted_outcome VARCHAR,                    -- Model's predicted outcome
prediction_confidence FLOAT CHECK (prediction_confidence >= 0 AND prediction_confidence <= 1),

-- Data quality and labeling
labeled_at TIMESTAMPTZ,                      -- When ground truth label was assigned
labeled_by TEXT,                             -- Who/what assigned the label
labeling_method VARCHAR CHECK (labeling_method IN ('automatic', 'analyst', 'backfill')),
data_quality_score FLOAT CHECK (data_quality_score >= 0 AND data_quality_score <= 1),

-- Training metadata
used_for_training BOOLEAN DEFAULT FALSE,     -- Whether included in training set
training_split VARCHAR CHECK (training_split IN ('train', 'validation', 'test')),
feature_extraction_version VARCHAR;          -- Version of feature extraction used

-- Add ML prediction logging to lifecycle history
ALTER TABLE pattern_lifecycle_history ADD COLUMN IF NOT EXISTS
ml_prediction JSONB DEFAULT '{}'::jsonb,     -- ML model prediction at transition time
prediction_latency_ms INTEGER,               -- Inference latency
model_version VARCHAR,                        -- Model version used
feature_vector JSONB DEFAULT '{}'::jsonb;    -- Features used for prediction

-- Create indexes for ML queries
CREATE INDEX IF NOT EXISTS idx_pattern_events_outcome_label 
ON pattern_events(outcome_label) WHERE outcome_label IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_pattern_events_ml_confidence 
ON pattern_events(ml_confidence) WHERE ml_confidence IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_pattern_events_training 
ON pattern_events(used_for_training, training_split) 
WHERE used_for_training = TRUE;

CREATE INDEX IF NOT EXISTS idx_pattern_events_labeled 
ON pattern_events(labeled_at, labeling_method) 
WHERE labeled_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_pattern_events_model_version 
ON pattern_events(ml_model_version) 
WHERE ml_model_version IS NOT NULL;

-- Create ML-specific tables for model management
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR NOT NULL UNIQUE,
    model_type VARCHAR NOT NULL,              -- 'gradient_boosting', 'neural_net', etc.
    model_path TEXT NOT NULL,                 -- Path to serialized model file
    training_data_hash VARCHAR,               -- Hash of training data for reproducibility
    hyperparameters JSONB DEFAULT '{}'::jsonb,
    training_metrics JSONB DEFAULT '{}'::jsonb,
    validation_metrics JSONB DEFAULT '{}'::jsonb,
    feature_importance JSONB DEFAULT '{}'::jsonb,
    model_card JSONB DEFAULT '{}'::jsonb,     -- Model documentation
    is_production BOOLEAN DEFAULT FALSE,      -- Whether this model is in production
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    deployment_notes TEXT
);

CREATE INDEX idx_ml_models_version ON ml_models(version);
CREATE INDEX idx_ml_models_production ON ml_models(is_production) WHERE is_production = TRUE;

-- Create table for prediction monitoring
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID NOT NULL REFERENCES pattern_events(id) ON DELETE CASCADE,
    model_version VARCHAR NOT NULL,
    prediction_type VARCHAR NOT NULL,         -- 'confidence', 'outcome', 'target_price'
    predicted_value FLOAT,
    predicted_class VARCHAR,
    confidence_score FLOAT,
    feature_vector JSONB DEFAULT '{}'::jsonb,
    inference_latency_ms INTEGER,
    prediction_timestamp TIMESTAMPTZ DEFAULT NOW(),
    actual_outcome FLOAT,                     -- Filled in later when known
    prediction_error FLOAT,                   -- |predicted - actual|
    outcome_timestamp TIMESTAMPTZ            -- When actual outcome was recorded
);

CREATE INDEX idx_ml_predictions_pattern_id ON ml_predictions(pattern_id);
CREATE INDEX idx_ml_predictions_model_version ON ml_predictions(model_version);
CREATE INDEX idx_ml_predictions_timestamp ON ml_predictions(prediction_timestamp DESC);
CREATE INDEX idx_ml_predictions_error ON ml_predictions(prediction_error) WHERE prediction_error IS NOT NULL;

-- Create table for feature store
CREATE TABLE IF NOT EXISTS ml_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID NOT NULL REFERENCES pattern_events(id) ON DELETE CASCADE,
    feature_version VARCHAR NOT NULL,
    feature_set_name VARCHAR NOT NULL,       -- 'technical_indicators', 'price_action', etc.
    features JSONB NOT NULL,
    extraction_timestamp TIMESTAMPTZ DEFAULT NOW(),
    extraction_duration_ms INTEGER,
    feature_quality_score FLOAT CHECK (feature_quality_score >= 0 AND feature_quality_score <= 1)
);

CREATE INDEX idx_ml_features_pattern_id ON ml_features(pattern_id);
CREATE INDEX idx_ml_features_version ON ml_features(feature_version);
CREATE INDEX idx_ml_features_set_name ON ml_features(feature_set_name);

-- Functions for ML operations

-- Function to get training data
CREATE OR REPLACE FUNCTION get_training_data(
    p_pattern_types TEXT[] DEFAULT NULL,
    p_min_data_quality FLOAT DEFAULT 0.7,
    p_labeled_only BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    pattern_id UUID,
    symbol TEXT,
    pattern_type TEXT,
    outcome_label VARCHAR,
    ml_features JSONB,
    realized_pnl FLOAT,
    target_accuracy FLOAT,
    confidence FLOAT,
    training_split VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pe.id as pattern_id,
        pe.symbol,
        pe.pattern_type,
        pe.outcome_label,
        pe.ml_features,
        pe.realized_pnl,
        pe.target_accuracy,
        pe.confidence,
        pe.training_split
    FROM pattern_events pe
    WHERE (p_pattern_types IS NULL OR pe.pattern_type = ANY(p_pattern_types))
        AND (NOT p_labeled_only OR pe.outcome_label IS NOT NULL)
        AND (pe.data_quality_score IS NULL OR pe.data_quality_score >= p_min_data_quality)
        AND pe.used_for_training = TRUE
    ORDER BY pe.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to log ML predictions
CREATE OR REPLACE FUNCTION log_ml_prediction(
    p_pattern_id UUID,
    p_model_version VARCHAR,
    p_prediction_type VARCHAR,
    p_predicted_value FLOAT,
    p_confidence_score FLOAT,
    p_feature_vector JSONB,
    p_inference_latency_ms INTEGER
)
RETURNS UUID AS $$
DECLARE
    v_prediction_id UUID;
BEGIN
    INSERT INTO ml_predictions (
        pattern_id,
        model_version,
        prediction_type,
        predicted_value,
        confidence_score,
        feature_vector,
        inference_latency_ms
    ) VALUES (
        p_pattern_id,
        p_model_version,
        p_prediction_type,
        p_predicted_value,
        p_confidence_score,
        p_feature_vector,
        p_inference_latency_ms
    ) RETURNING id INTO v_prediction_id;
    
    RETURN v_prediction_id;
END;
$$ LANGUAGE plpgsql;

-- Function to update prediction with actual outcome
CREATE OR REPLACE FUNCTION update_prediction_outcome(
    p_prediction_id UUID,
    p_actual_outcome FLOAT
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE ml_predictions
    SET actual_outcome = p_actual_outcome,
        prediction_error = ABS(predicted_value - p_actual_outcome),
        outcome_timestamp = NOW()
    WHERE id = p_prediction_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to get model performance metrics
CREATE OR REPLACE FUNCTION get_model_performance(
    p_model_version VARCHAR,
    p_days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    total_predictions BIGINT,
    avg_prediction_error FLOAT,
    rmse FLOAT,
    mae FLOAT,
    accuracy_within_5pct FLOAT,
    avg_inference_latency_ms FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_predictions,
        AVG(prediction_error) as avg_prediction_error,
        SQRT(AVG(prediction_error * prediction_error)) as rmse,
        AVG(ABS(prediction_error)) as mae,
        AVG(CASE WHEN ABS(prediction_error) <= 0.05 THEN 1.0 ELSE 0.0 END) as accuracy_within_5pct,
        AVG(inference_latency_ms::FLOAT) as avg_inference_latency_ms
    FROM ml_predictions
    WHERE model_version = p_model_version
        AND prediction_timestamp >= NOW() - INTERVAL '1 day' * p_days_back
        AND actual_outcome IS NOT NULL;
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE ml_models IS 'Model registry for ML pattern confidence models';
COMMENT ON TABLE ml_predictions IS 'Prediction logging for monitoring and evaluation';
COMMENT ON TABLE ml_features IS 'Feature store for ML training and inference';
COMMENT ON FUNCTION get_training_data IS 'Extract labeled training data for model development';
COMMENT ON FUNCTION log_ml_prediction IS 'Log ML prediction for monitoring';
COMMENT ON FUNCTION get_model_performance IS 'Calculate model performance metrics';