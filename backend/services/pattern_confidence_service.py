"""
Pattern Confidence Service - Phase 5 ML Inference
===============================================
Real-time ML inference service for pattern confidence prediction with caching and fallbacks
"""

import logging
import json
import time
import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np
import joblib

try:  # pragma: no cover - optional dependency
    from supabase import create_client, Client
except ImportError:  # pragma: no cover - optional dependency
    create_client = None
    Client = None

# Import ML feature builder
from .ml.feature_builder import PatternFeatureBuilder, FeatureSet

# Import monitoring
from .ml_monitoring import get_ml_monitoring

logger = logging.getLogger(__name__)

@dataclass
class ConfidencePrediction:
    """Container for ML confidence prediction results"""
    ml_confidence: float
    prediction_class: str
    class_probabilities: Dict[str, float]
    feature_count: int
    model_version: str
    inference_latency_ms: int
    fallback_used: bool
    rule_confidence: Optional[float] = None
    blended_confidence: Optional[float] = None
    explanation: Optional[Dict[str, Any]] = None

class PatternConfidenceService:
    """
    Machine Learning inference service for pattern confidence prediction
    
    Features:
    - Model loading and hot-reloading
    - Feature extraction integration
    - Prediction caching for performance
    - Fallback to rule-based confidence
    - Latency monitoring (<75ms SLA)
    - Prediction logging for monitoring
    - SHAP explanations for interpretability
    """
    
    def __init__(self,
                 model_path: Optional[str] = None,
                 cache_size: int = 1000,
                 enable_cache: bool = True,
                 fallback_confidence: float = 0.5,
                 blend_weights: Optional[Dict[str, float]] = None):
        """
        Initialize Pattern Confidence Service
        
        Args:
            model_path: Path to trained model directory (None for auto-discovery)
            cache_size: Maximum number of cached predictions
            enable_cache: Whether to enable prediction caching
            fallback_confidence: Default confidence when ML fails
            blend_weights: Weights for blending ML and rule confidence
        """
        self.model_path = model_path
        self.cache_size = cache_size
        self.enable_cache = enable_cache
        self.fallback_confidence = fallback_confidence
        
        # Default blend weights: 70% ML, 30% rules
        self.blend_weights = blend_weights or {"ml": 0.7, "rule": 0.3}
        
        # Model artifacts
        self.model = None
        self.scalers = None
        self.label_encoders = None
        self.model_metadata = None
        self.feature_names: Optional[List[str]] = None
        
        # Services
        self.feature_builder = PatternFeatureBuilder()
        self.monitoring = get_ml_monitoring()
        
        # Caching
        self.prediction_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Performance monitoring
        self.prediction_count = 0
        self.total_latency_ms = 0
        self.error_count = 0
        
        # Optional Supabase client for prediction logging
        self.supabase_client = self._init_supabase_client()
        
        # Initialize model
        asyncio.create_task(self._load_model())
    
    async def _load_model(self):
        """Load ML model and associated artifacts"""
        try:
            model_dir = self._discover_model_path()
            if not model_dir:
                logger.warning("No trained model found - using fallback confidence only")
                return
            
            logger.info(f"Loading ML model from {model_dir}")
            
            # Load model artifacts
            model_file = model_dir / "model.pkl"
            scalers_file = model_dir / "scalers.pkl"
            encoders_file = model_dir / "encoders.pkl"
            metadata_file = model_dir / "model_card.json"
            
            if model_file.exists():
                self.model = joblib.load(model_file)
                logger.info("✓ Model loaded successfully")
            
            if scalers_file.exists():
                self.scalers = joblib.load(scalers_file)
                logger.info("✓ Scalers loaded")
            if encoders_file.exists():
                self.label_encoders = joblib.load(encoders_file)
                logger.info("✓ Label encoders loaded")
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.model_metadata = json.load(f)
                logger.info(
                    "✓ Model metadata loaded: %s",
                    self.model_metadata.get("model_version", "unknown")
                )

            # Extract feature names from metadata or use defaults
            if self.model_metadata:
                feature_names = self.model_metadata.get("feature_names")
                if feature_names:
                    self.feature_names = feature_names
                else:
                    self.feature_names = self.feature_builder.feature_names
            else:
                self.feature_names = self.feature_builder.feature_names

            logger.info("ML model ready for inference")
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {str(e)}")
            self.model = None
    
    def _discover_model_path(self) -> Optional[Path]:
        """Discover the path to the trained model"""
        if self.model_path:
            return Path(self.model_path)
        
        # Look for champion model in standard locations
        champion_dirs = [
            Path("models/phase5/champion"),
            Path("backend/models/phase5/champion"),
            Path("/app/models/phase5/champion")  # Docker path
        ]
        
        for champion_dir in champion_dirs:
            if champion_dir.exists() and (champion_dir / "model.pkl").exists():
                return champion_dir
        
        # Look for latest model
        models_dirs = [
            Path("models/phase5"),
            Path("backend/models/phase5")
        ]
        
        for models_dir in models_dirs:
            if models_dir.exists():
                # Find latest timestamp directory
                timestamp_dirs = [d for d in models_dir.iterdir() 
                                if d.is_dir() and d.name != "champion"]
                if timestamp_dirs:
                    latest_dir = max(timestamp_dirs, key=lambda x: x.name)
                    model_files = list(latest_dir.glob("*_model.pkl"))
                    if model_files:
                        return latest_dir
        
        return None
    
    async def predict_confidence(self,
                               pattern_data: Dict[str, Any],
                               price_history: Optional[List[Dict]] = None,
                               market_data: Optional[Dict[str, Any]] = None,
                               rule_confidence: Optional[float] = None) -> ConfidencePrediction:
        """
        Predict pattern confidence using ML model with fallback
        
        Args:
            pattern_data: Pattern metadata
            price_history: Recent price data for technical features
            market_data: Market context data
            rule_confidence: Rule-based confidence for blending
            
        Returns:
            ConfidencePrediction with ML confidence and metadata
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(pattern_data)
            if self.enable_cache and cache_key in self.prediction_cache:
                self.cache_hits += 1
                cached_prediction = self.prediction_cache[cache_key]
                cached_prediction.inference_latency_ms = int((time.time() - start_time) * 1000)
                
                # Record monitoring metrics for cached prediction
                self.monitoring.record_inference(
                    latency_ms=cached_prediction.inference_latency_ms,
                    confidence=cached_prediction.ml_confidence,
                    prediction_class=cached_prediction.prediction_class,
                    ml_used=not cached_prediction.fallback_used,
                    error_occurred=False,
                    cache_hit=True,
                    features=None  # Features not available for cached predictions
                )
                
                return cached_prediction
            
            self.cache_misses += 1
            
            # Extract features
            feature_set = self.feature_builder.extract_features(
                pattern_data=pattern_data,
                price_history=price_history,
                market_data=market_data
            )
            
            # ML prediction
            if self.model and feature_set.quality_score > 0.5:
                prediction = await self._ml_predict(feature_set)
                prediction.fallback_used = False
            else:
                # Fallback to rule-based confidence
                prediction = self._fallback_predict(rule_confidence or self.fallback_confidence)
                prediction.fallback_used = True
            
            # Blend with rule confidence if available
            if rule_confidence is not None and not prediction.fallback_used:
                prediction.rule_confidence = rule_confidence
                prediction.blended_confidence = self._blend_confidences(
                    prediction.ml_confidence, rule_confidence
                )
            
            # Calculate latency
            prediction.inference_latency_ms = int((time.time() - start_time) * 1000)
            
            # Cache prediction
            if self.enable_cache:
                self._cache_prediction(cache_key, prediction)
            
            # Update monitoring stats
            self.prediction_count += 1
            self.total_latency_ms += prediction.inference_latency_ms
            
            # Log prediction for monitoring
            await self._log_prediction(pattern_data, prediction, feature_set.features)
            
            # Record monitoring metrics
            self.monitoring.record_inference(
                latency_ms=prediction.inference_latency_ms,
                confidence=prediction.ml_confidence,
                prediction_class=prediction.prediction_class,
                ml_used=not prediction.fallback_used,
                error_occurred=False,
                cache_hit=cache_key in self.prediction_cache,
                features=feature_set.features if 'feature_set' in locals() else None
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            self.error_count += 1
            
            # Return fallback prediction
            fallback = self._fallback_predict(rule_confidence or self.fallback_confidence)
            fallback.inference_latency_ms = int((time.time() - start_time) * 1000)
            fallback.fallback_used = True
            
            # Record monitoring metrics for error case
            self.monitoring.record_inference(
                latency_ms=fallback.inference_latency_ms,
                confidence=fallback.ml_confidence,
                prediction_class=fallback.prediction_class,
                ml_used=False,
                error_occurred=True,
                cache_hit=False,
                features=None
            )
            
            return fallback
    
    async def _ml_predict(self, feature_set: FeatureSet) -> ConfidencePrediction:
        """Perform ML model prediction"""
        if not self.model:
            raise ValueError("ML model not loaded")
        
        # Prepare feature vector
        feature_vector = self._prepare_feature_vector(feature_set)
        
        # Apply scaling if needed
        if self.scalers and 'logistic_scaler' in self.scalers and hasattr(self.scalers['logistic_scaler'], 'transform'):
            feature_vector = self.scalers['logistic_scaler'].transform([feature_vector])
        else:
            feature_vector = [feature_vector]
        
        # Predict
        probabilities = self.model.predict_proba(feature_vector)[0]
        predicted_class_idx = np.argmax(probabilities)
        
        # Map class index to label
        if self.label_encoders and 'label_encoder' in self.label_encoders:
            class_labels = self.label_encoders['label_encoder'].classes_
            predicted_class = class_labels[predicted_class_idx]
            class_probs = dict(zip(class_labels, probabilities))
        else:
            predicted_class = f"class_{predicted_class_idx}"
            class_probs = {f"class_{i}": prob for i, prob in enumerate(probabilities)}
        
        # Convert to confidence score (0-1)
        if predicted_class == "positive":
            ml_confidence = probabilities[predicted_class_idx]
        elif predicted_class == "negative":
            ml_confidence = 1.0 - probabilities[predicted_class_idx]
        else:  # neutral
            ml_confidence = 0.5
        
        # Get model version
        model_version = self.model_metadata.get('model_version', 'unknown') if self.model_metadata else 'unknown'
        
        return ConfidencePrediction(
            ml_confidence=ml_confidence,
            prediction_class=predicted_class,
            class_probabilities=class_probs,
            feature_count=len(feature_set.features),
            model_version=model_version,
            inference_latency_ms=0,  # Set by caller
            fallback_used=False
        )
    
    def _fallback_predict(self, rule_confidence: float) -> ConfidencePrediction:
        """Generate fallback prediction when ML unavailable"""
        return ConfidencePrediction(
            ml_confidence=rule_confidence,
            prediction_class="neutral",
            class_probabilities={"neutral": 1.0},
            feature_count=0,
            model_version="fallback",
            inference_latency_ms=0,  # Set by caller
            fallback_used=True,
            rule_confidence=rule_confidence
        )
    
    def _prepare_feature_vector(self, feature_set: FeatureSet) -> List[float]:
        """Prepare feature vector for model prediction"""
        if not self.feature_names:
            # Use feature set order
            return list(feature_set.features.values())
        
        # Ensure features are in the correct order
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(feature_set.features.get(feature_name, 0.0))
        
        return feature_vector
    
    def _blend_confidences(self, ml_confidence: float, rule_confidence: float) -> float:
        """Blend ML and rule-based confidences"""
        ml_weight = self.blend_weights.get("ml", 0.7)
        rule_weight = self.blend_weights.get("rule", 0.3)
        
        blended = (ml_confidence * ml_weight) + (rule_confidence * rule_weight)
        return max(0.0, min(1.0, blended))  # Clamp to [0, 1]
    
    def _generate_cache_key(self, pattern_data: Dict[str, Any]) -> str:
        """Generate cache key for prediction"""
        # Use pattern characteristics for caching
        key_parts = [
            pattern_data.get("pattern_type", ""),
            str(pattern_data.get("support", 0)),
            str(pattern_data.get("resistance", 0)),
            str(pattern_data.get("target", 0)),
            str(pattern_data.get("confidence", 0))
        ]
        return "_".join(key_parts)
    
    def _cache_prediction(self, cache_key: str, prediction: ConfidencePrediction):
        """Cache prediction result"""
        if len(self.prediction_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.prediction_cache))
            del self.prediction_cache[oldest_key]
        
        self.prediction_cache[cache_key] = prediction
    
    def _init_supabase_client(self) -> Optional[Client]:  # pragma: no cover - network guarded
        """Initialize Supabase client for prediction logging."""
        if create_client is None:
            logger.debug("Supabase SDK not available; ML predictions will not be persisted")
            return None

        url = os.getenv("SUPABASE_URL")
        key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
        )
        if not url or not key:
            logger.debug("Supabase credentials missing; ML predictions will not be persisted")
            return None

        try:
            client = create_client(url, key)
            logger.info("Supabase client initialized for ML prediction logging")
            return client
        except Exception as exc:
            logger.warning("Failed to initialize Supabase client: %s", exc)
            return None

    async def _log_prediction(
        self,
        pattern_data: Dict[str, Any],
        prediction: ConfidencePrediction,
        features: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log prediction locally and, if configured, to Supabase."""
        if prediction.fallback_used:
            return

        try:
            pattern_id = (
                pattern_data.get("pattern_id")
                or pattern_data.get("id")
                or pattern_data.get("patternId")
            )

            if not pattern_id:
                logger.debug("Skipping ML prediction log; pattern_id missing")
                return

            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pattern_id": pattern_id,
                "symbol": pattern_data.get("symbol"),
                "pattern_type": pattern_data.get("pattern_type"),
                "ml_confidence": prediction.ml_confidence,
                "prediction_class": prediction.prediction_class,
                "model_version": prediction.model_version,
                "inference_latency_ms": prediction.inference_latency_ms,
                "fallback_used": prediction.fallback_used,
                "feature_count": prediction.feature_count,
            }
            logger.debug("Prediction logged: %s", json.dumps(log_entry))

            if not self.supabase_client:
                return

            safe_features: Dict[str, Any] = {}
            if features:
                for key, value in features.items():
                    safe_features[key] = float(value) if isinstance(value, (int, float)) else value

            payload = {
                "p_pattern_id": pattern_id,
                "p_model_version": prediction.model_version,
                "p_prediction_type": "confidence",
                "p_predicted_value": prediction.blended_confidence
                if prediction.blended_confidence is not None
                else prediction.ml_confidence,
                "p_confidence_score": prediction.ml_confidence,
                "p_feature_vector": safe_features,
                "p_inference_latency_ms": prediction.inference_latency_ms,
            }

            loop = asyncio.get_running_loop()

            def _execute_rpc():
                self.supabase_client.rpc("log_ml_prediction", payload).execute()

            await loop.run_in_executor(None, _execute_rpc)

        except Exception as exc:
            logger.warning("Failed to log prediction: %s", exc)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service performance statistics"""
        avg_latency = (self.total_latency_ms / self.prediction_count) if self.prediction_count > 0 else 0
        cache_hit_rate = (self.cache_hits / (self.cache_hits + self.cache_misses)) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        return {
            "model_loaded": self.model is not None,
            "model_version": self.model_metadata.get('model_version', 'unknown') if self.model_metadata else 'none',
            "predictions_made": self.prediction_count,
            "average_latency_ms": round(avg_latency, 2),
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.prediction_count) if self.prediction_count > 0 else 0,
            "cache_enabled": self.enable_cache,
            "cache_size": len(self.prediction_cache),
            "cache_hit_rate": round(cache_hit_rate, 3),
            "blend_weights": self.blend_weights,
            "feature_count": len(self.feature_names) if self.feature_names else 0
        }
    
    async def reload_model(self, model_path: Optional[str] = None) -> bool:
        """Hot-reload model for updates"""
        try:
            old_model_version = self.model_metadata.get('model_version', 'unknown') if self.model_metadata else 'none'
            
            if model_path:
                self.model_path = model_path
            
            await self._load_model()
            
            new_model_version = self.model_metadata.get('model_version', 'unknown') if self.model_metadata else 'none'
            
            # Clear cache on model reload
            self.prediction_cache.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            
            logger.info(f"Model reloaded: {old_model_version} → {new_model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Model reload failed: {str(e)}")
            return False
    
    def clear_cache(self):
        """Clear prediction cache"""
        self.prediction_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Prediction cache cleared")

# Singleton service instance
_confidence_service_instance = None

def get_confidence_service() -> PatternConfidenceService:
    """Get or create singleton confidence service instance"""
    global _confidence_service_instance
    if _confidence_service_instance is None:
        _confidence_service_instance = PatternConfidenceService()
    return _confidence_service_instance

def configure_confidence_service(**kwargs) -> PatternConfidenceService:
    """Configure and get confidence service with custom settings"""
    global _confidence_service_instance
    _confidence_service_instance = PatternConfidenceService(**kwargs)
    return _confidence_service_instance