# Phase 5 ML Monitoring Plan

## Overview
This document outlines the monitoring infrastructure plan for Phase 5 ML-driven pattern confidence enhancement before production enablement.

## Pre-Deployment Validation Status

### ✅ Completed Tasks
1. **Environment Variables Configured**
   - Added to `backend/.env` with safe defaults
   - `ENABLE_PHASE5_ML=false` (disabled by default for gradual rollout)
   - ML confidence weights configured (60% ML, 40% rule-based)
   - Confidence threshold set to 0.55

2. **Directory Structure Created**
   - Champion model directory: `backend/models/phase5/champion/`
   - Ready for model artifacts

### ⚠️ Pending Tasks

1. **Database Migration**
   - Migration file exists: `supabase/migrations/20250928000001_phase5_ml_columns.sql`
   - Status: NOT YET APPLIED
   - Action Required: Run migration through Supabase dashboard or CLI
   
2. **Model Training**
   - Champion artifacts directory is EMPTY
   - Action Required: Train initial models before enabling Phase 5
   ```bash
   cd backend
   PYTHONPATH=. python ml/pattern_confidence.py --models random_forest logistic
   ```

3. **Monitoring Infrastructure Setup**
   - Endpoints implemented but not yet monitored
   - Action Required: Configure monitoring dashboards

## Monitoring Infrastructure

### 1. Health Check Endpoint
**Endpoint**: `GET /api/ml/health`

**Monitors**:
- Model loading status
- Inference service availability
- Feature builder status
- Cache health
- Fallback mechanism status

**Alert Thresholds**:
- Model not loaded: CRITICAL
- Cache unavailable: WARNING
- Fallback rate > 10%: WARNING

### 2. Performance Metrics Endpoint
**Endpoint**: `GET /api/ml/metrics`

**Key Metrics**:
- **Inference Latency**: Target < 75ms, Alert > 100ms
- **Cache Hit Rate**: Target > 80%, Alert < 60%
- **ML Usage Rate**: Track adoption percentage
- **Fallback Rate**: Target < 10%, Alert > 20%
- **Error Rate**: Target < 5%, Alert > 10%

**Response Format**:
```json
{
  "current": {
    "inference_latency_p50": 45,
    "inference_latency_p95": 72,
    "cache_hit_rate": 0.85,
    "ml_usage_rate": 0.92,
    "fallback_rate": 0.08,
    "error_rate": 0.02
  },
  "history": [...]
}
```

### 3. Drift Detection Endpoint
**Endpoint**: `GET /api/ml/alerts`

**Monitors**:
- Feature distribution drift
- Prediction distribution changes
- Model performance degradation
- Data quality issues

**Alert Types**:
- DRIFT_DETECTED: Feature distributions shifted
- PERFORMANCE_DEGRADED: Model accuracy dropped
- DATA_QUALITY_ISSUE: Invalid features detected

### 4. Baseline Management
**Endpoint**: `POST /api/ml/baseline`

**Purpose**: Set reference point for drift detection after deployment

**Usage**:
```bash
# After successful deployment and initial validation
curl -X POST http://localhost:8000/api/ml/baseline
```

## Monitoring Dashboard Requirements

### Grafana Dashboard Panels

1. **Real-time Performance**
   - Inference latency histogram (p50, p95, p99)
   - Request rate and throughput
   - Cache hit/miss ratio
   - Active inference count

2. **Model Health**
   - ML vs Rule confidence distribution
   - Fallback trigger reasons
   - Model version in use
   - Feature extraction success rate

3. **Business Metrics**
   - Pattern confidence accuracy
   - False positive/negative rates
   - User adoption metrics
   - API usage by endpoint

4. **System Resources**
   - Memory usage (model loading)
   - CPU utilization (inference)
   - Disk I/O (model artifact loading)
   - Network latency (if using remote models)

### Alert Configuration

**PagerDuty Integration**:
```yaml
alerts:
  - name: ml_inference_latency_high
    condition: p95_latency > 100ms for 5 minutes
    severity: WARNING
    
  - name: ml_service_unavailable
    condition: health_check fails for 2 minutes
    severity: CRITICAL
    
  - name: high_fallback_rate
    condition: fallback_rate > 20% for 10 minutes
    severity: WARNING
    
  - name: model_drift_detected
    condition: feature_drift_score > 0.3
    severity: INFO
```

## Rollout Monitoring Strategy

### Phase 1: Canary Deployment (Day 1-3)
- Enable for 5% of traffic
- Monitor all metrics closely
- Baseline establishment
- Daily performance reviews

### Phase 2: Gradual Rollout (Day 4-7)
- Increase to 25% traffic
- A/B testing metrics
- Performance comparison with Phase 4
- User feedback collection

### Phase 3: Full Deployment (Day 8+)
- 100% traffic with Phase 5
- Continuous monitoring
- Weekly model performance reviews
- Monthly retraining evaluation

## Logging Requirements

### Structured Logging Format
```json
{
  "timestamp": "2025-09-28T10:30:45Z",
  "service": "pattern_confidence",
  "level": "INFO",
  "event": "inference_complete",
  "pattern_id": "uuid",
  "model_version": "v1.2.0",
  "inference_latency_ms": 45,
  "confidence_ml": 0.85,
  "confidence_rule": 0.72,
  "confidence_blended": 0.80,
  "cache_hit": true,
  "features_count": 52
}
```

### Log Retention
- **Production Logs**: 30 days hot storage, 90 days cold storage
- **ML Predictions**: 180 days for model evaluation
- **Performance Metrics**: 1 year aggregated, 30 days raw

## Pre-Enablement Checklist

Before setting `ENABLE_PHASE5_ML=true`:

- [ ] Database migration applied successfully
- [ ] Champion model artifacts trained and deployed
- [ ] Monitoring dashboards configured
- [ ] Alert channels configured
- [ ] Baseline metrics established
- [ ] Rollback procedure tested
- [ ] Team briefed on monitoring procedures

## Emergency Procedures

### Immediate Rollback
```bash
# Disable ML enhancement instantly
export ENABLE_PHASE5_ML=false
# Restart backend service
systemctl restart backend-service
```

### Performance Degradation Response
1. Check `/api/ml/health` endpoint
2. Review `/api/ml/metrics` for anomalies
3. Check logs for error patterns
4. If inference latency > 150ms, trigger fallback
5. If error rate > 15%, disable ML enhancement

### Model Issues
- Missing artifacts: System auto-falls back to rules
- Corrupted model: Load backup from `models/phase5/backup/`
- Version mismatch: Check `model_card.json` for compatibility

## Success Criteria

Phase 5 is considered successfully deployed when:
- ✅ Inference latency p95 < 75ms for 24 hours
- ✅ Fallback rate < 10% for 48 hours
- ✅ Error rate < 5% sustained
- ✅ Cache hit rate > 80%
- ✅ No critical alerts for 72 hours
- ✅ Positive user feedback on confidence accuracy

## Contact Information

**On-Call Rotation**: See PagerDuty schedule
**Escalation**: ML Team Lead → Platform Team → CTO
**Documentation**: `backend/README_phase5.md`
**Runbooks**: `/docs/runbooks/phase5-ml-operations.md`

---

*Last Updated: Sep 28, 2025*
*Status: READY FOR DEPLOYMENT PENDING MIGRATION AND TRAINING*