"""
ML Confidence Enhancer - Phase 5 Integration
===========================================
Clean separation of ML enhancement from core pattern lifecycle logic
"""

import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .pattern_confidence_service import get_confidence_service, ConfidencePrediction

logger = logging.getLogger(__name__)

@dataclass
class EnhancedConfidence:
    """Result of ML confidence enhancement"""
    final_confidence: float
    rule_confidence: float
    ml_confidence: Optional[float] = None
    blended_confidence: Optional[float] = None
    ml_prediction_class: Optional[str] = None
    ml_model_version: Optional[str] = None
    prediction_latency_ms: Optional[int] = None
    fallback_used: bool = False
    ml_metadata: Optional[Dict[str, Any]] = None

class MLConfidenceEnhancer:
    """
    Enhances pattern confidence using ML predictions
    
    Clean separation of concerns:
    - Core lifecycle logic remains unchanged
    - ML enhancement is optional and pluggable
    - Graceful fallback to rule-based confidence
    """
    
    def __init__(self, enable_ml: bool = True):
        self.enable_ml = enable_ml
        self.confidence_service = get_confidence_service() if enable_ml else None
        self.prediction_count = 0
        self.error_count = 0
    
    async def enhance_confidence(self, 
                               pattern: Dict[str, Any], 
                               rule_confidence: float) -> EnhancedConfidence:
        """
        Enhance pattern confidence with ML prediction
        
        Args:
            pattern: Pattern data
            rule_confidence: Original rule-based confidence (0-100)
            
        Returns:
            EnhancedConfidence with ML-enhanced or fallback confidence
        """
        
        # Normalize rule confidence to 0-1 range
        normalized_rule = rule_confidence / 100.0 if rule_confidence > 1.0 else rule_confidence
        
        if not self.enable_ml or not self.confidence_service:
            return EnhancedConfidence(
                final_confidence=rule_confidence,
                rule_confidence=rule_confidence,
                fallback_used=True
            )
        
        try:
            # Get ML prediction
            ml_prediction = await self._get_ml_prediction(pattern, normalized_rule)
            self.prediction_count += 1
            
            # Convert back to percentage for consistency with existing code
            final_confidence = (
                ml_prediction.blended_confidence * 100
                if ml_prediction.blended_confidence is not None
                else ml_prediction.ml_confidence * 100
            )
            
            return EnhancedConfidence(
                final_confidence=final_confidence,
                rule_confidence=rule_confidence,
                ml_confidence=ml_prediction.ml_confidence,
                blended_confidence=ml_prediction.blended_confidence,
                ml_prediction_class=ml_prediction.prediction_class,
                ml_model_version=ml_prediction.model_version,
                prediction_latency_ms=ml_prediction.inference_latency_ms,
                fallback_used=ml_prediction.fallback_used,
                ml_metadata={
                    "feature_count": ml_prediction.feature_count,
                    "class_probabilities": ml_prediction.class_probabilities
                }
            )
            
        except Exception as e:
            logger.warning(f"ML confidence enhancement failed: {str(e)}")
            self.error_count += 1
            return EnhancedConfidence(
                final_confidence=rule_confidence,
                rule_confidence=rule_confidence,
                fallback_used=True
            )
    
    async def _get_ml_prediction(self, 
                               pattern: Dict[str, Any], 
                               rule_confidence: float) -> ConfidencePrediction:
        """Get ML prediction for pattern"""
        
        # Prepare pattern data for ML service
        pattern_data = {
            "id": pattern.get("id"),
            "pattern_type": pattern.get("pattern_type", pattern.get("category", "unknown")),
            "symbol": pattern.get("symbol"),
            "timeframe": pattern.get("timeframe"),
            "support": pattern.get("support", 0.0),
            "resistance": pattern.get("resistance", 0.0),
            "target": pattern.get("target", 0.0),
            "confidence": rule_confidence,
            "volume": pattern.get("volume", 0.0),
            "strength": pattern.get("strength", 0.0),
            "key_levels": pattern.get("key_levels", {}),
            "targets": pattern.get("targets", []),
            "metadata": pattern.get("metadata", {})
        }
        
        # Extract additional data if available
        price_history = pattern.get("price_history")
        market_data = pattern.get("market_data")
        
        return await self.confidence_service.predict_confidence(
            pattern_data=pattern_data,
            price_history=price_history,
            market_data=market_data,
            rule_confidence=rule_confidence
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhancement statistics"""
        error_rate = self.error_count / self.prediction_count if self.prediction_count > 0 else 0
        
        return {
            "ml_enabled": self.enable_ml,
            "predictions_made": self.prediction_count,
            "error_count": self.error_count,
            "error_rate": round(error_rate, 3),
            "service_loaded": self.confidence_service is not None
        }

# Singleton instance
_ml_enhancer_instance = None

def get_ml_enhancer(enable_ml: bool = True) -> MLConfidenceEnhancer:
    """Get or create singleton ML enhancer instance"""
    global _ml_enhancer_instance
    if _ml_enhancer_instance is None:
        _ml_enhancer_instance = MLConfidenceEnhancer(enable_ml=enable_ml)
    return _ml_enhancer_instance