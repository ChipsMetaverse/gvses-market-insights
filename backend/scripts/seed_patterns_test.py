#!/usr/bin/env python3
"""
Pattern Seeding Script
======================
Seeds test patterns into the system to verify ML logging path.
Can be used to test PatternLifecycleManager -> PatternConfidenceService -> Supabase flow.
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
from uuid import uuid4

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import services
from services.pattern_lifecycle import PatternLifecycleManager
from services.pattern_repository import PatternRepository
from services.pattern_structured_adapter import PatternStructuredAdapter
from services.pattern_confidence_service import PatternConfidenceService

def generate_test_patterns(symbol: str = "AAPL", count: int = 5) -> List[Dict[str, Any]]:
    """Generate test patterns with varying confidence levels."""
    patterns = []
    
    pattern_templates = [
        {
            "pattern_type": "bullish_engulfing",
            "signal": "bullish",
            "base_confidence": 0.75,
            "description": "Strong bullish engulfing pattern detected"
        },
        {
            "pattern_type": "breakout",
            "signal": "bullish",
            "base_confidence": 0.80,
            "description": "Breakout above resistance at $150"
        },
        {
            "pattern_type": "double_bottom",
            "signal": "bullish",
            "base_confidence": 0.70,
            "description": "Double bottom formation completed"
        },
        {
            "pattern_type": "support_bounce",
            "signal": "bullish",
            "base_confidence": 0.65,
            "description": "Bounce off support at $145"
        },
        {
            "pattern_type": "head_shoulders",
            "signal": "bearish",
            "base_confidence": 0.72,
            "description": "Head and shoulders pattern forming"
        }
    ]
    
    for i in range(min(count, len(pattern_templates))):
        template = pattern_templates[i]
        pattern_id = str(uuid4())
        
        pattern = {
            "id": pattern_id,
            "pattern_id": pattern_id,
            "symbol": symbol,
            "timeframe": "1D",
            "pattern_type": template["pattern_type"],
            "confidence": template["base_confidence"],
            "status": "pending",
            "signal": template["signal"],
            "description": template["description"],
            "support": 145.0 + i,
            "resistance": 150.0 + i,
            "target": 155.0 + i if template["signal"] == "bullish" else 140.0 - i,
            "stop_loss": 143.0 + i if template["signal"] == "bullish" else 152.0 + i,
            "entry": 147.5 + i,
            "metadata": {
                "source": "test_seeder",
                "test_run": True,
                "creation_time": datetime.now(timezone.utc).isoformat()
            },
            "auto_generated": True,
            "ml_eligible": True
        }
        
        patterns.append(pattern)
    
    return patterns

async def test_ml_logging_path(patterns: List[Dict[str, Any]]):
    """Test the full ML logging path."""
    print("\n" + "=" * 60)
    print("Testing ML Logging Path")
    print("=" * 60)
    
    # Initialize services
    print("\n1. Initializing services...")
    lifecycle_manager = PatternLifecycleManager()
    repository = PatternRepository()
    
    # Check if Phase 5 is enabled
    enable_ml = os.getenv("ENABLE_PHASE5_ML", "false").lower() == "true"
    print(f"   Phase 5 ML: {'ENABLED' if enable_ml else 'DISABLED'}")
    
    if not enable_ml:
        print("\n⚠️ Phase 5 ML is disabled. Set ENABLE_PHASE5_ML=true to test ML path")
        print("   Patterns will use rule-based confidence only")
    
    # Process each pattern through the lifecycle
    print(f"\n2. Processing {len(patterns)} test patterns...")
    results = []
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n   Pattern {i}/{len(patterns)}: {pattern['pattern_type']}")
        print(f"   - Symbol: {pattern['symbol']}")
        print(f"   - Rule Confidence: {pattern['confidence']:.2f}")
        
        try:
            # Store pattern in repository
            if repository.client:
                pattern_id = await repository.create_pattern(pattern)
                if pattern_id:
                    print(f"   - Stored in DB: {pattern_id}")
                    pattern["id"] = pattern_id
                    pattern["pattern_id"] = pattern_id
            
            # Process through lifecycle manager (triggers ML if enabled)
            enhanced = await lifecycle_manager.process_pattern(pattern)
            
            if enhanced:
                ml_conf = enhanced.get("ml_confidence")
                blended = enhanced.get("blended_confidence")
                
                if ml_conf is not None:
                    print(f"   - ML Confidence: {ml_conf:.2f}")
                    print(f"   - Blended Confidence: {blended:.2f}")
                    print(f"   - ML Model: {enhanced.get('ml_model_version', 'N/A')}")
                else:
                    print(f"   - Final Confidence: {enhanced.get('confidence', pattern['confidence']):.2f}")
                
                results.append({
                    "pattern_type": pattern["pattern_type"],
                    "rule_confidence": pattern["confidence"],
                    "ml_confidence": ml_conf,
                    "blended_confidence": blended,
                    "ml_used": ml_conf is not None
                })
            else:
                print(f"   - Pattern processing failed")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if results:
        ml_enhanced = sum(1 for r in results if r["ml_used"])
        print(f"\nPatterns processed: {len(results)}")
        print(f"ML enhanced: {ml_enhanced}")
        print(f"Rule-only: {len(results) - ml_enhanced}")
        
        if ml_enhanced > 0:
            avg_rule = sum(r["rule_confidence"] for r in results) / len(results)
            ml_results = [r for r in results if r["ml_used"]]
            avg_ml = sum(r["ml_confidence"] for r in ml_results) / len(ml_results)
            avg_blended = sum(r["blended_confidence"] for r in ml_results) / len(ml_results)
            
            print(f"\nAverage Confidences:")
            print(f"  Rule-based: {avg_rule:.3f}")
            print(f"  ML: {avg_ml:.3f}")
            print(f"  Blended: {avg_blended:.3f}")
    
    return results

async def verify_supabase_logging():
    """Verify if predictions are being logged to Supabase."""
    print("\n" + "=" * 60)
    print("Verifying Supabase Logging")
    print("=" * 60)
    
    repository = PatternRepository()
    
    if not repository.client:
        print("\n❌ Supabase client not initialized")
        print("   Check SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        return
    
    try:
        # Check if ml_predictions table exists
        result = repository.client.table("ml_predictions").select("*").limit(5).execute()
        
        if result.data:
            print(f"\n✅ Found {len(result.data)} recent ML predictions in database")
            for pred in result.data:
                print(f"   - Pattern: {pred.get('pattern_id', 'N/A')[:8]}... "
                      f"Model: {pred.get('model_version', 'N/A')} "
                      f"Confidence: {pred.get('confidence_score', 0):.2f}")
        else:
            print("\n⚠️ No ML predictions found in database")
            print("   This is expected if:")
            print("   - Phase 5 is disabled (ENABLE_PHASE5_ML=false)")
            print("   - Database migration not applied")
            print("   - No patterns have been processed yet")
            
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("\n❌ ml_predictions table does not exist")
            print("   Apply migration: supabase/migrations/20250928000001_phase5_ml_columns.sql")
        else:
            print(f"\n❌ Error checking predictions: {str(e)}")

async def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("Phase 5 ML Pattern Seeding Test")
    print("=" * 60)
    
    # Check environment
    from dotenv import load_dotenv
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"\n✅ Loaded environment from: {env_path}")
    else:
        print(f"\n⚠️ No .env file found at: {env_path}")
    
    # Generate test patterns
    print("\n1. Generating test patterns...")
    patterns = generate_test_patterns(symbol="TEST", count=3)
    print(f"   Generated {len(patterns)} patterns")
    
    # Test ML logging path
    results = await test_ml_logging_path(patterns)
    
    # Verify Supabase logging
    await verify_supabase_logging()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    
    if not os.getenv("ENABLE_PHASE5_ML", "false").lower() == "true":
        print("\n📝 To enable ML enhancement:")
        print("   1. Set ENABLE_PHASE5_ML=true in backend/.env")
        print("   2. Apply database migration if not done")
        print("   3. Run this script again")

if __name__ == "__main__":
    asyncio.run(main())