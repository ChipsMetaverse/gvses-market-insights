# Phase 5 ML Testing Guide

## Overview

This guide provides comprehensive testing procedures for Phase 5 ML-driven pattern confidence enhancement. Phase 5 introduces machine learning capabilities to improve pattern confidence scoring while maintaining robust fallback mechanisms and comprehensive observability.

## Test Suite Structure

### Core Components Tested

1. **ML Feature Extraction Pipeline** (`backend/services/ml/feature_builder.py`)
2. **Model Training Pipeline** (`backend/ml/pattern_confidence.py`)
3. **Real-time Inference Service** (`backend/services/pattern_confidence_service.py`)
4. **ML Confidence Enhancement** (`backend/services/ml_confidence_enhancer.py`)
5. **Lifecycle Integration** (`backend/services/pattern_lifecycle.py`)
6. **Production Monitoring** (`backend/services/ml_monitoring.py`)

### Test Categories

- **Unit Tests**: Individual component functionality
- **Integration Tests**: Component interaction and data flow
- **Performance Tests**: Latency and throughput validation
- **Regression Tests**: Comprehensive system validation
- **Benchmark Tests**: Performance baseline establishment

## Running Tests

### Prerequisites

```bash
# Install testing dependencies
cd backend
pip install pytest pytest-asyncio pytest-benchmark psutil

# Install ML dependencies
pip install scikit-learn xgboost lightgbm joblib pandas numpy
```

### Test Execution

#### Full Test Suite
```bash
cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py -v
```

#### Specific Test Categories
```bash
# Feature extraction tests
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py::TestPhase5FeatureExtraction -v

# ML service tests
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py::TestPhase5InferenceService -v

# Integration tests
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py::TestPhase5LifecycleIntegration -v

# Performance tests
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py::TestPhase5Performance -v

# Error handling tests
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py::TestPhase5ErrorHandling -v
```

#### CI/CD Testing
```bash
# Run the full Phase 5 CI/CD pipeline
gh workflow run phase5-ml-pipeline.yml
```

## Test Validation Criteria

### Performance Requirements

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Inference Latency** | <75ms | Automated SLA testing |
| **Feature Extraction** | 50 features | Completeness validation |
| **Model Accuracy** | >70% | Cross-validation testing |
| **Fallback Rate** | <5% | Production monitoring |
| **Cache Hit Rate** | >80% | Performance benchmarks |
| **Error Rate** | <1% | Comprehensive error testing |

### Feature Quality Standards

```python
# Feature extraction validation
def validate_feature_quality(feature_set):
    assert len(feature_set.features) == 50
    assert feature_set.quality_score > 0.5
    assert all(isinstance(v, (int, float)) for v in feature_set.features.values())
    assert all(not (isinstance(v, float) and v != v) for v in feature_set.features.values())  # No NaN
    assert all(abs(v) < 1e10 for v in feature_set.features.values())  # No extreme values
```

### ML Service Health Checks

```python
# Service health validation
def validate_ml_service_health(service_stats):
    assert service_stats["model_loaded"] == True or service_stats["fallback_rate"] < 1.0
    assert service_stats["error_rate"] < 0.05
    assert service_stats["average_latency_ms"] < 75
    assert service_stats["cache_hit_rate"] > 0.6  # Reasonable cache performance
```

## Manual Testing Procedures

### 1. Feature Extraction Testing

```python
# Test feature extraction manually
from backend.services.ml.feature_builder import PatternFeatureBuilder

builder = PatternFeatureBuilder()
pattern = {
    'pattern_type': 'ascending_triangle',
    'support': 150.0,
    'resistance': 160.0,
    'target': 170.0,
    'confidence': 0.75,
    'symbol': 'TSLA'
}

features = builder.extract_features(pattern_data=pattern)
print(f"✅ Extracted {len(features.features)} features")
print(f"✅ Quality score: {features.quality_score:.3f}")
```

### 2. ML Inference Testing

```python
# Test ML confidence enhancement
import asyncio
from backend.services.ml_confidence_enhancer import MLConfidenceEnhancer

async def test_ml_enhancement():
    enhancer = MLConfidenceEnhancer(enable_ml=True)
    
    pattern = {
        'pattern_type': 'ascending_triangle',
        'support': 150.0,
        'resistance': 160.0,
        'confidence': 65.0,
        'symbol': 'TSLA'
    }
    
    enhanced = await enhancer.enhance_confidence(pattern, 65.0)
    
    print(f"✅ Rule confidence: {enhanced.rule_confidence}")
    print(f"✅ Final confidence: {enhanced.final_confidence:.2f}")
    print(f"✅ Fallback used: {enhanced.fallback_used}")

asyncio.run(test_ml_enhancement())
```

### 3. Integration Testing

```python
# Test full lifecycle integration
import asyncio
from backend.services.pattern_lifecycle import PatternLifecycleManager

async def test_lifecycle_integration():
    manager = PatternLifecycleManager(
        enable_phase4_rules=False,
        enable_phase5_ml=True
    )
    
    pattern = {
        'pattern_id': 'test_001',
        'pattern_type': 'ascending_triangle',
        'confidence': 65.0,
        'support': 150.0,
        'resistance': 160.0,
        'symbol': 'TSLA',
        'timeframe': '1h'
    }
    
    analysis = {'patterns': [pattern]}
    result = await manager.update(
        symbol='TSLA',
        timeframe='1h',
        analysis=analysis
    )
    
    print(f"✅ States: {len(result['states'])}")
    print(f"✅ Commands: {len(result['chart_commands'])}")

asyncio.run(test_lifecycle_integration())
```

### 4. Performance Validation

```python
# Validate SLA compliance
import asyncio
import time
from backend.services.ml_confidence_enhancer import MLConfidenceEnhancer

async def validate_sla():
    enhancer = MLConfidenceEnhancer(enable_ml=True)
    pattern = {
        'pattern_type': 'ascending_triangle',
        'support': 150.0, 'resistance': 160.0,
        'confidence': 65.0, 'symbol': 'TSLA'
    }
    
    # Warm up
    await enhancer.enhance_confidence(pattern, 65.0)
    
    # Measure latency
    latencies = []
    for i in range(10):
        start = time.time()
        await enhancer.enhance_confidence(pattern, 65.0)
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    
    print(f'✅ Average latency: {avg_latency:.2f}ms')
    print(f'✅ Max latency: {max_latency:.2f}ms')
    
    assert max_latency < 75, f"SLA violation: {max_latency:.2f}ms > 75ms"
    print(f'✅ SLA validated: All predictions < 75ms')

asyncio.run(validate_sla())
```

## Monitoring and Observability Testing

### 1. ML Metrics Validation

```bash
# Test ML metrics endpoint
curl http://localhost:8000/api/ml/metrics

# Expected response structure:
{
  "current": {
    "performance": {
      "inference_count": 0,
      "avg_latency_ms": 0.0,
      "error_rate": 0.0,
      "sla_compliance": 1.0
    },
    "confidence": {
      "mean": 0.0,
      "std": 0.0,
      "p50": 0.0,
      "p95": 0.0,
      "p99": 0.0
    },
    "predictions": {
      "ml_predictions": 0,
      "fallback_predictions": 0,
      "fallback_rate": 0.0
    },
    "health": {
      "status": "healthy",
      "baseline_set": false
    }
  }
}
```

### 2. Health Check Validation

```bash
# Test ML health endpoint
curl http://localhost:8000/api/ml/health

# Expected healthy response:
{
  "status": "healthy",
  "phase5_enabled": true,
  "model_loaded": false,
  "error_rate": 0.0,
  "sla_compliance": 1.0,
  "fallback_rate": 0.0
}
```

### 3. Alert System Testing

```bash
# Test ML alerts endpoint
curl http://localhost:8000/api/ml/alerts

# Expected response:
{
  "alerts": [],
  "count": 0,
  "timestamp": "2025-09-28T..."
}
```

## Troubleshooting Guide

### Common Issues

#### 1. Import Errors
```bash
# Symptom: ModuleNotFoundError for ML dependencies
# Solution: Install ML dependencies
pip install scikit-learn xgboost lightgbm joblib pandas numpy
```

#### 2. Test Path Issues
```bash
# Symptom: Import errors in tests
# Solution: Set PYTHONPATH correctly
cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp
PYTHONPATH=. python -m pytest backend/tests/test_phase5_regression.py
```

#### 3. Performance Issues
```bash
# Symptom: Tests failing SLA requirements
# Check: System resource usage
# Solution: Run on machine with adequate CPU/memory
```

#### 4. Model Loading Issues
```bash
# Symptom: Model not found warnings
# Expected: System should gracefully fall back to rule-based confidence
# Validation: Check fallback_used=True in prediction responses
```

### Debugging Commands

```python
# Debug feature extraction
from backend.services.ml.feature_builder import PatternFeatureBuilder
builder = PatternFeatureBuilder()
print(f"Feature names: {builder.feature_names}")

# Debug ML service
from backend.services.pattern_confidence_service import get_confidence_service
service = get_confidence_service()
stats = service.get_service_stats()
print(f"Service stats: {stats}")

# Debug monitoring
from backend.services.ml_monitoring import get_ml_monitoring
monitoring = get_ml_monitoring()
current = await monitoring.get_current_metrics()
print(f"Current metrics: {current}")
```

## Test Result Interpretation

### Success Criteria

✅ **All tests pass** with the following validations:
- Feature extraction produces 50 features consistently
- ML inference completes within 75ms SLA
- Fallback mechanisms work when ML unavailable
- Integration with lifecycle manager successful
- Monitoring and observability functional

### Expected Warnings

⚠️ **Normal warnings** (non-blocking):
- "No trained model found - using fallback confidence only"
- "ML prediction failed for pattern X: ..." (with graceful fallback)
- Cache misses on first runs

### Failure Indicators

❌ **Test failures** requiring investigation:
- SLA violations (>75ms inference)
- Feature extraction producing <50 features
- Integration errors between components
- Monitoring service unavailable
- High error rates without fallback

## Performance Benchmarks

### Baseline Performance Targets

| Component | Metric | Target | Tolerance |
|-----------|--------|--------|-----------|
| Feature Extraction | Time | <10ms | ±5ms |
| ML Inference | Latency | <75ms | ±10ms |
| Cache Hit | Response | <5ms | ±2ms |
| Fallback | Response | <20ms | ±5ms |
| Monitoring | Update | <100ms | ±20ms |

### Load Testing

```python
# Concurrent inference test
import asyncio
from backend.services.pattern_confidence_service import PatternConfidenceService

async def load_test():
    service = PatternConfidenceService()
    
    patterns = [
        {"pattern_type": "ascending_triangle", "support": 100+i, "resistance": 110+i}
        for i in range(50)
    ]
    
    start_time = time.time()
    tasks = [service.predict_confidence(pattern) for pattern in patterns]
    predictions = await asyncio.gather(*tasks)
    end_time = time.time()
    
    total_time = (end_time - start_time) * 1000
    avg_latency = total_time / len(patterns)
    
    print(f"✅ {len(predictions)} predictions in {total_time:.2f}ms")
    print(f"✅ Average: {avg_latency:.2f}ms per prediction")

asyncio.run(load_test())
```

## Continuous Integration

### GitHub Actions Workflow

The Phase 5 CI/CD pipeline (`phase5-ml-pipeline.yml`) runs:

1. **Dependency Installation**: ML packages and testing tools
2. **Feature Tests**: Validation of 50-feature extraction
3. **Service Tests**: ML inference and caching functionality
4. **Integration Tests**: Lifecycle manager with ML enhancement
5. **Performance Tests**: SLA compliance validation
6. **Error Handling**: Graceful degradation testing
7. **Security Scan**: ML dependency vulnerability checks

### Manual CI Trigger

```bash
# Trigger full Phase 5 pipeline
gh workflow run phase5-ml-pipeline.yml

# Trigger with model training
gh workflow run phase5-ml-pipeline.yml -f run_training=true

# Trigger with benchmarks
gh workflow run phase5-ml-pipeline.yml -f run_benchmarks=true
```

## Production Deployment Validation

### Pre-deployment Checklist

- [ ] All Phase 5 regression tests pass
- [ ] Performance benchmarks meet SLA requirements
- [ ] Monitoring endpoints functional
- [ ] Fallback mechanisms validated
- [ ] Error handling tested
- [ ] Documentation updated

### Post-deployment Monitoring

```bash
# Validate production deployment
curl https://your-domain.com/api/ml/health
curl https://your-domain.com/api/ml/metrics
curl https://your-domain.com/api/ml/alerts
```

### Rollback Procedures

If Phase 5 deployment issues occur:

1. **Disable ML Enhancement**: Set `enable_phase5_ml=False` in configuration
2. **Verify Fallback**: Confirm system operates with rule-based confidence only
3. **Monitor Metrics**: Check `/api/ml/health` shows graceful degradation
4. **Investigate**: Review logs and monitoring data for root cause

Phase 5 is designed with robust fallback mechanisms to ensure system reliability even when ML components experience issues.

---

## Summary

Phase 5 ML testing covers:
- ✅ Comprehensive feature extraction validation
- ✅ Real-time ML inference with SLA compliance
- ✅ Robust fallback and error handling
- ✅ Complete integration with existing systems
- ✅ Production monitoring and observability
- ✅ Automated CI/CD validation

The testing suite ensures Phase 5 ML enhancements maintain system reliability while providing improved pattern confidence scoring through machine learning.