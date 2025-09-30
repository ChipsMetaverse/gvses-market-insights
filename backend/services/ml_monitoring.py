"""
Phase 5 ML Monitoring & Observability
===================================
Production monitoring for ML-driven pattern confidence enhancement

Features:
- Real-time ML performance metrics
- Model drift detection
- Confidence distribution tracking
- Error rate monitoring
- SLA compliance tracking
- Model performance dashboards
"""

import logging
import json
import time
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class MLMetrics:
    """ML performance metrics container"""
    timestamp: datetime
    inference_count: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    sla_violations: int = 0
    sla_compliance: float = 1.0
    
    # Confidence distribution
    confidence_mean: float = 0.0
    confidence_std: float = 0.0
    confidence_p50: float = 0.0
    confidence_p95: float = 0.0
    confidence_p99: float = 0.0
    
    # Model usage
    ml_predictions: int = 0
    fallback_predictions: int = 0
    fallback_rate: float = 0.0
    
    # Prediction classes
    positive_predictions: int = 0
    negative_predictions: int = 0
    neutral_predictions: int = 0
    
    # Cache performance
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0

@dataclass
class DriftMetrics:
    """Model drift detection metrics"""
    timestamp: datetime
    feature_drift_score: float = 0.0
    prediction_drift_score: float = 0.0
    confidence_drift_score: float = 0.0
    drift_alert_level: str = "normal"  # normal, warning, critical
    features_analyzed: int = 0
    drift_features: List[str] = field(default_factory=list)

class MLMonitoringService:
    """
    Production monitoring service for Phase 5 ML components
    
    Tracks:
    - Inference performance and SLA compliance
    - Model drift and data quality
    - Error rates and fallback usage
    - Confidence distribution changes
    - Cache performance and efficiency
    """
    
    def __init__(self, 
                 sla_threshold_ms: float = 75.0,
                 drift_window_hours: int = 24,
                 metrics_retention_hours: int = 168):  # 7 days
        self.sla_threshold_ms = sla_threshold_ms
        self.drift_window_hours = drift_window_hours
        self.metrics_retention_hours = metrics_retention_hours
        
        # Real-time metrics storage
        self.current_metrics = MLMetrics(timestamp=datetime.now(timezone.utc))
        self.metrics_history: deque = deque(maxlen=metrics_retention_hours * 60)  # Per minute
        
        # Drift detection
        self.baseline_features: Optional[Dict[str, float]] = None
        self.recent_features: deque = deque(maxlen=1000)  # Last 1000 predictions
        self.drift_history: deque = deque(maxlen=drift_window_hours * 60)
        
        # Real-time tracking
        self.latencies: deque = deque(maxlen=1000)
        self.confidences: deque = deque(maxlen=1000)
        self.prediction_classes: deque = deque(maxlen=1000)
        self.errors: deque = deque(maxlen=100)
        
        # Counters (reset every minute)
        self.reset_counters()
        
        # Background tasks
        self._monitoring_task = None
        self._start_monitoring()
    
    def reset_counters(self):
        """Reset per-minute counters"""
        self.minute_inference_count = 0
        self.minute_error_count = 0
        self.minute_sla_violations = 0
        self.minute_ml_predictions = 0
        self.minute_fallback_predictions = 0
        self.minute_cache_hits = 0
        self.minute_cache_misses = 0
        
        self.minute_positive = 0
        self.minute_negative = 0
        self.minute_neutral = 0
    
    def record_inference(self, 
                        latency_ms: float,
                        confidence: float,
                        prediction_class: str,
                        ml_used: bool,
                        error_occurred: bool = False,
                        cache_hit: bool = False,
                        features: Optional[Dict[str, float]] = None):
        """Record ML inference metrics"""
        
        # Update real-time tracking
        self.latencies.append(latency_ms)
        self.confidences.append(confidence)
        self.prediction_classes.append(prediction_class)
        
        if features:
            self.recent_features.append(features)
        
        # Update counters
        self.minute_inference_count += 1
        
        if error_occurred:
            self.minute_error_count += 1
            self.errors.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "latency_ms": latency_ms,
                "confidence": confidence,
                "ml_used": ml_used
            })
        
        if latency_ms > self.sla_threshold_ms:
            self.minute_sla_violations += 1
        
        if ml_used:
            self.minute_ml_predictions += 1
        else:
            self.minute_fallback_predictions += 1
        
        if cache_hit:
            self.minute_cache_hits += 1
        else:
            self.minute_cache_misses += 1
        
        # Update prediction class counters
        if prediction_class == "positive":
            self.minute_positive += 1
        elif prediction_class == "negative":
            self.minute_negative += 1
        else:
            self.minute_neutral += 1
    
    def _calculate_metrics(self) -> MLMetrics:
        """Calculate current metrics from tracked data"""
        now = datetime.now(timezone.utc)
        
        # Latency metrics
        avg_latency = statistics.mean(self.latencies) if self.latencies else 0.0
        max_latency = max(self.latencies) if self.latencies else 0.0
        
        # Error metrics
        error_rate = (
            self.minute_error_count / self.minute_inference_count 
            if self.minute_inference_count > 0 else 0.0
        )
        
        # SLA metrics
        sla_compliance = (
            1.0 - (self.minute_sla_violations / self.minute_inference_count)
            if self.minute_inference_count > 0 else 1.0
        )
        
        # Confidence distribution
        confidence_mean = statistics.mean(self.confidences) if self.confidences else 0.0
        confidence_std = statistics.stdev(self.confidences) if len(self.confidences) > 1 else 0.0
        
        sorted_confidences = sorted(self.confidences) if self.confidences else [0.0]
        confidence_p50 = statistics.median(sorted_confidences)
        confidence_p95 = sorted_confidences[int(len(sorted_confidences) * 0.95)] if sorted_confidences else 0.0
        confidence_p99 = sorted_confidences[int(len(sorted_confidences) * 0.99)] if sorted_confidences else 0.0
        
        # Fallback rate
        total_predictions = self.minute_ml_predictions + self.minute_fallback_predictions
        fallback_rate = (
            self.minute_fallback_predictions / total_predictions
            if total_predictions > 0 else 0.0
        )
        
        # Cache performance
        total_requests = self.minute_cache_hits + self.minute_cache_misses
        cache_hit_rate = (
            self.minute_cache_hits / total_requests
            if total_requests > 0 else 0.0
        )
        
        return MLMetrics(
            timestamp=now,
            inference_count=self.minute_inference_count,
            avg_latency_ms=avg_latency,
            max_latency_ms=max_latency,
            error_count=self.minute_error_count,
            error_rate=error_rate,
            sla_violations=self.minute_sla_violations,
            sla_compliance=sla_compliance,
            confidence_mean=confidence_mean,
            confidence_std=confidence_std,
            confidence_p50=confidence_p50,
            confidence_p95=confidence_p95,
            confidence_p99=confidence_p99,
            ml_predictions=self.minute_ml_predictions,
            fallback_predictions=self.minute_fallback_predictions,
            fallback_rate=fallback_rate,
            positive_predictions=self.minute_positive,
            negative_predictions=self.minute_negative,
            neutral_predictions=self.minute_neutral,
            cache_hits=self.minute_cache_hits,
            cache_misses=self.minute_cache_misses,
            cache_hit_rate=cache_hit_rate
        )
    
    def _detect_drift(self) -> DriftMetrics:
        """Detect model and data drift"""
        now = datetime.now(timezone.utc)
        
        if not self.recent_features or len(self.recent_features) < 100:
            return DriftMetrics(timestamp=now, drift_alert_level="insufficient_data")
        
        # Calculate feature drift if we have baseline
        feature_drift_score = 0.0
        drift_features = []
        
        if self.baseline_features:
            feature_drifts = []
            
            # Compare recent features to baseline
            recent_features_dict = defaultdict(list)
            for feature_set in list(self.recent_features)[-100:]:  # Last 100 predictions
                for name, value in feature_set.items():
                    recent_features_dict[name].append(value)
            
            for feature_name, baseline_mean in self.baseline_features.items():
                if feature_name in recent_features_dict and recent_features_dict[feature_name]:
                    recent_mean = statistics.mean(recent_features_dict[feature_name])
                    drift = abs(recent_mean - baseline_mean) / (abs(baseline_mean) + 1e-8)
                    feature_drifts.append(drift)
                    
                    if drift > 0.5:  # Significant drift threshold
                        drift_features.append(feature_name)
            
            feature_drift_score = statistics.mean(feature_drifts) if feature_drifts else 0.0
        
        # Calculate prediction drift
        recent_confidences = list(self.confidences)[-100:]
        recent_classes = list(self.prediction_classes)[-100:]
        
        prediction_drift_score = 0.0
        if len(recent_confidences) > 50:
            # Simple drift detection based on confidence distribution change
            recent_mean = statistics.mean(recent_confidences)
            recent_std = statistics.stdev(recent_confidences) if len(recent_confidences) > 1 else 0.0
            
            # Compare to historical if available
            if len(self.metrics_history) > 0:
                historical_means = [m.confidence_mean for m in list(self.metrics_history)[-60:]]  # Last hour
                if historical_means:
                    historical_mean = statistics.mean(historical_means)
                    prediction_drift_score = abs(recent_mean - historical_mean) / (historical_mean + 1e-8)
        
        # Overall drift assessment
        overall_drift = max(feature_drift_score, prediction_drift_score)
        
        if overall_drift > 0.8:
            alert_level = "critical"
        elif overall_drift > 0.5:
            alert_level = "warning"
        else:
            alert_level = "normal"
        
        return DriftMetrics(
            timestamp=now,
            feature_drift_score=feature_drift_score,
            prediction_drift_score=prediction_drift_score,
            confidence_drift_score=prediction_drift_score,  # Simplified
            drift_alert_level=alert_level,
            features_analyzed=len(self.baseline_features) if self.baseline_features else 0,
            drift_features=drift_features
        )
    
    def set_baseline(self, features: Dict[str, float]):
        """Set baseline feature distribution for drift detection"""
        self.baseline_features = features.copy()
        logger.info(f"Set ML monitoring baseline with {len(features)} features")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current ML metrics"""
        metrics = self._calculate_metrics()
        drift = self._detect_drift()
        
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "performance": {
                "inference_count": metrics.inference_count,
                "avg_latency_ms": round(metrics.avg_latency_ms, 2),
                "max_latency_ms": round(metrics.max_latency_ms, 2),
                "error_rate": round(metrics.error_rate, 3),
                "sla_compliance": round(metrics.sla_compliance, 3),
                "sla_violations": metrics.sla_violations
            },
            "confidence": {
                "mean": round(metrics.confidence_mean, 3),
                "std": round(metrics.confidence_std, 3),
                "p50": round(metrics.confidence_p50, 3),
                "p95": round(metrics.confidence_p95, 3),
                "p99": round(metrics.confidence_p99, 3)
            },
            "predictions": {
                "ml_predictions": metrics.ml_predictions,
                "fallback_predictions": metrics.fallback_predictions,
                "fallback_rate": round(metrics.fallback_rate, 3),
                "positive": metrics.positive_predictions,
                "negative": metrics.negative_predictions,
                "neutral": metrics.neutral_predictions
            },
            "cache": {
                "hits": metrics.cache_hits,
                "misses": metrics.cache_misses,
                "hit_rate": round(metrics.cache_hit_rate, 3)
            },
            "drift": {
                "feature_drift_score": round(drift.feature_drift_score, 3),
                "prediction_drift_score": round(drift.prediction_drift_score, 3),
                "alert_level": drift.drift_alert_level,
                "drift_features": drift.drift_features
            },
            "health": {
                "status": "healthy" if metrics.error_rate < 0.05 and metrics.sla_compliance > 0.95 else "degraded",
                "recent_errors": len(self.errors),
                "baseline_set": self.baseline_features is not None
            }
        }
    
    async def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp >= cutoff
        ]
        
        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "inference_count": m.inference_count,
                "avg_latency_ms": round(m.avg_latency_ms, 2),
                "error_rate": round(m.error_rate, 3),
                "sla_compliance": round(m.sla_compliance, 3),
                "confidence_mean": round(m.confidence_mean, 3),
                "fallback_rate": round(m.fallback_rate, 3)
            }
            for m in recent_metrics
        ]
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts and warnings"""
        alerts = []
        current_metrics = self._calculate_metrics()
        drift_metrics = self._detect_drift()
        
        # SLA violations
        if current_metrics.sla_compliance < 0.95:
            alerts.append({
                "level": "warning" if current_metrics.sla_compliance > 0.90 else "critical",
                "type": "sla_violation",
                "message": f"SLA compliance at {current_metrics.sla_compliance:.1%}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # High error rate
        if current_metrics.error_rate > 0.1:
            alerts.append({
                "level": "critical" if current_metrics.error_rate > 0.2 else "warning",
                "type": "high_error_rate",
                "message": f"Error rate at {current_metrics.error_rate:.1%}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # High fallback rate
        if current_metrics.fallback_rate > 0.5:
            alerts.append({
                "level": "warning",
                "type": "high_fallback_rate", 
                "message": f"Fallback rate at {current_metrics.fallback_rate:.1%}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Model drift
        if drift_metrics.drift_alert_level in ["warning", "critical"]:
            alerts.append({
                "level": drift_metrics.drift_alert_level,
                "type": "model_drift",
                "message": f"Model drift detected: {drift_metrics.feature_drift_score:.2f}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "drift_features": drift_metrics.drift_features
            })
        
        return alerts
    
    def _start_monitoring(self):
        """Start background monitoring task"""
        async def monitoring_loop():
            while True:
                try:
                    # Calculate and store metrics every minute
                    metrics = self._calculate_metrics()
                    self.metrics_history.append(metrics)
                    self.current_metrics = metrics
                    
                    # Calculate drift
                    drift = self._detect_drift()
                    self.drift_history.append(drift)
                    
                    # Reset counters for next minute
                    self.reset_counters()
                    
                    # Log summary every 10 minutes
                    if len(self.metrics_history) % 10 == 0:
                        logger.info(
                            f"ML Monitoring: {metrics.inference_count} inferences, "
                            f"{metrics.avg_latency_ms:.1f}ms avg latency, "
                            f"{metrics.error_rate:.1%} error rate, "
                            f"{metrics.sla_compliance:.1%} SLA compliance"
                        )
                    
                    await asyncio.sleep(60)  # 1 minute intervals
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {str(e)}")
                    await asyncio.sleep(30)
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(monitoring_loop())
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()

# Singleton monitoring service
_ml_monitoring_instance = None

def get_ml_monitoring() -> MLMonitoringService:
    """Get or create singleton ML monitoring service"""
    global _ml_monitoring_instance
    if _ml_monitoring_instance is None:
        _ml_monitoring_instance = MLMonitoringService()
    return _ml_monitoring_instance

def configure_ml_monitoring(**kwargs) -> MLMonitoringService:
    """Configure ML monitoring with custom settings"""
    global _ml_monitoring_instance
    if _ml_monitoring_instance:
        _ml_monitoring_instance.stop_monitoring()
    _ml_monitoring_instance = MLMonitoringService(**kwargs)
    return _ml_monitoring_instance