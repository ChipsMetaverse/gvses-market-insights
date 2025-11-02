#!/usr/bin/env python3
"""
Enhanced Knowledge Loader

Loads the enhanced_pattern_knowledge_base.json and provides
integration with the existing _enrich_with_knowledge() function.

This bridges the 123-pattern knowledge base with the pattern detector.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class EnhancedPatternKnowledge:
    """
    Loads and provides access to the enhanced pattern knowledge base
    containing 123 patterns with Bulkowski statistics, trading playbooks,
    and invalidation rules.
    """
    
    def __init__(self, kb_path: str = "training/enhanced_pattern_knowledge_base.json"):
        self.kb_path = Path(__file__).parent / kb_path
        self.patterns: Dict[str, Any] = {}
        self.loaded = False
        self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> None:
        """Load the enhanced knowledge base JSON file"""
        try:
            if not self.kb_path.exists():
                logger.warning(f"Enhanced knowledge base not found at {self.kb_path}")
                return
            
            with open(self.kb_path, 'r') as f:
                data = json.load(f)
            
            self.patterns = data.get("patterns", {})
            self.loaded = True
            
            logger.info(f"✅ Loaded enhanced knowledge base: {len(self.patterns)} patterns")
            logger.info(f"   Sources: {', '.join(data.get('sources', []))}")
            
        except Exception as e:
            logger.error(f"Failed to load enhanced knowledge base: {e}")
            self.loaded = False
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pattern data by ID.
        
        Args:
            pattern_id: Pattern identifier (e.g., "head_and_shoulders_top")
        
        Returns:
            Pattern dict or None if not found
        """
        if not self.loaded:
            return None
        
        # Try exact match first
        pattern_id_lower = pattern_id.lower()
        if pattern_id_lower in self.patterns:
            return self.patterns[pattern_id_lower]
        
        # Try with underscores replaced
        normalized = pattern_id_lower.replace("-", "_").replace(" ", "_")
        if normalized in self.patterns:
            return self.patterns[normalized]
        
        return None
    
    def get_success_rate(self, pattern_id: str, market_type: str = "bull") -> Optional[float]:
        """
        Get Bulkowski success rate for a pattern.
        
        Args:
            pattern_id: Pattern identifier
            market_type: "bull" or "bear"
        
        Returns:
            Success rate percentage (0-100) or None
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        stats = pattern.get("statistics", {})
        
        if market_type == "bull":
            return stats.get("bull_market_success_rate")
        elif market_type == "bear":
            return stats.get("bear_market_success_rate")
        else:
            # Return average of bull and bear if available
            bull = stats.get("bull_market_success_rate")
            bear = stats.get("bear_market_success_rate")
            if bull is not None and bear is not None:
                return (bull + bear) / 2
            return bull or bear
    
    def get_trading_playbook(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trading playbook with entry/exit rules.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Trading dict with entry_rules, exit_rules, stop_loss_guidance, etc.
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        return pattern.get("trading", {})
    
    def get_invalidation_rules(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pattern invalidation conditions and warning signs.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Invalidation dict with conditions and warning_signs
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        return pattern.get("invalidation", {})
    
    def get_bulkowski_rank(self, pattern_id: str) -> Optional[str]:
        """
        Get Bulkowski rank (A/B/C/D/F).
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Rank letter or None
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        return pattern.get("bulkowski_rank")
    
    def get_bulkowski_tier(self, pattern_id: str) -> Optional[str]:
        """
        Get Bulkowski tier (A/B/C/D/F).
        Alias for get_bulkowski_rank.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Tier letter or None
        """
        return self.get_bulkowski_rank(pattern_id)
    
    def get_risk_reward_ratio(self, pattern_id: str) -> Optional[float]:
        """
        Get expected risk/reward ratio.
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Risk/reward ratio (e.g., 2.5 = 2.5:1) or None
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        trading = pattern.get("trading", {})
        return trading.get("risk_reward_ratio")
    
    def get_typical_duration(self, pattern_id: str) -> Optional[str]:
        """
        Get typical pattern duration (e.g., "2-4 weeks").
        
        Args:
            pattern_id: Pattern identifier
        
        Returns:
            Duration string or None
        """
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return None
        
        trading = pattern.get("trading", {})
        return trading.get("typical_duration")
    
    def enrich_pattern_dict(self, pattern_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a pattern dictionary with enhanced knowledge base data.
        
        This is the integration point for the pattern detector's
        _enrich_with_knowledge() function.
        
        Args:
            pattern_dict: Pattern dictionary from detector
        
        Returns:
            Enriched pattern dictionary
        """
        if not self.loaded:
            return pattern_dict
        
        pattern_type = pattern_dict.get("pattern_type") or pattern_dict.get("type")
        if not pattern_type:
            return pattern_dict
        
        kb_pattern = self.get_pattern(pattern_type)
        if not kb_pattern:
            return pattern_dict
        
        # Add Bulkowski statistics
        stats = kb_pattern.get("statistics", {})
        if stats:
            pattern_dict["bulkowski_stats"] = {
                "bull_market_success_rate": stats.get("bull_market_success_rate"),
                "bear_market_success_rate": stats.get("bear_market_success_rate"),
                "average_rise": stats.get("average_rise"),
                "average_decline": stats.get("average_decline"),
                "failure_rate": stats.get("failure_rate"),
            }
        
        # Add trading playbook
        trading = kb_pattern.get("trading", {})
        if trading:
            if trading.get("entry_rules"):
                pattern_dict["entry_guidance"] = "; ".join(trading["entry_rules"])
            
            if trading.get("exit_rules"):
                pattern_dict["exit_guidance"] = "; ".join(trading["exit_rules"])
            
            pattern_dict["stop_loss_guidance"] = trading.get("stop_loss_guidance", "")
            pattern_dict["target_guidance"] = trading.get("target_guidance", "")
            pattern_dict["risk_reward_ratio"] = trading.get("risk_reward_ratio")
            pattern_dict["typical_duration"] = trading.get("typical_duration", "")
        
        # Add Bulkowski rank/tier
        pattern_dict["bulkowski_rank"] = kb_pattern.get("bulkowski_rank")
        pattern_dict["bulkowski_tier"] = kb_pattern.get("bulkowski_tier")
        
        # Add invalidation rules
        invalidation = kb_pattern.get("invalidation", {})
        if invalidation:
            if invalidation.get("conditions"):
                pattern_dict["invalidation_conditions"] = invalidation["conditions"]
            if invalidation.get("warning_signs"):
                pattern_dict["warning_signs"] = invalidation["warning_signs"]
        
        # Add strategy notes
        if trading.get("strategy_notes"):
            pattern_dict["strategy_notes"] = trading["strategy_notes"]
        
        # Add description and psychology
        if kb_pattern.get("description"):
            pattern_dict["description"] = kb_pattern["description"]
        
        if kb_pattern.get("psychology"):
            pattern_dict["psychology"] = kb_pattern["psychology"]
        
        return pattern_dict
    
    def get_patterns_by_category(self, category: str) -> List[str]:
        """
        Get all pattern IDs for a given category.
        
        Args:
            category: "candlestick", "chart_pattern", "price_action", "event_pattern"
        
        Returns:
            List of pattern IDs
        """
        if not self.loaded:
            return []
        
        return [
            pattern_id 
            for pattern_id, pattern in self.patterns.items()
            if pattern.get("category") == category
        ]
    
    def get_patterns_by_signal(self, signal: str) -> List[str]:
        """
        Get all pattern IDs for a given signal type.
        
        Args:
            signal: "bullish", "bearish", "neutral", "continuation", "reversal"
        
        Returns:
            List of pattern IDs
        """
        if not self.loaded:
            return []
        
        return [
            pattern_id 
            for pattern_id, pattern in self.patterns.items()
            if pattern.get("signal") == signal
        ]
    
    def get_high_success_patterns(self, min_success_rate: float = 70.0) -> List[tuple]:
        """
        Get patterns with success rate above threshold.
        
        Args:
            min_success_rate: Minimum success rate percentage
        
        Returns:
            List of (pattern_id, success_rate) tuples, sorted by success rate
        """
        if not self.loaded:
            return []
        
        high_success = []
        for pattern_id, pattern in self.patterns.items():
            stats = pattern.get("statistics", {})
            
            # Try to get highest available success rate
            success_rate = (
                stats.get("bull_market_success_rate") or 
                stats.get("bear_market_success_rate") or
                stats.get("success_rate")
            )
            
            if success_rate and success_rate >= min_success_rate:
                high_success.append((pattern_id, success_rate))
        
        # Sort by success rate descending
        high_success.sort(key=lambda x: x[1], reverse=True)
        return high_success


# Global instance
_enhanced_kb = None

def get_enhanced_knowledge() -> EnhancedPatternKnowledge:
    """Get or create the global enhanced knowledge instance"""
    global _enhanced_kb
    if _enhanced_kb is None:
        _enhanced_kb = EnhancedPatternKnowledge()
    return _enhanced_kb


if __name__ == "__main__":
    # Test the enhanced knowledge loader
    print("Testing Enhanced Knowledge Loader...")
    print("=" * 70)
    
    kb = EnhancedPatternKnowledge()
    
    if kb.loaded:
        print(f"✅ Loaded {len(kb.patterns)} patterns\n")
        
        # Test getting a specific pattern
        test_patterns = [
            "head_and_shoulders_top",
            "bullish_engulfing",
            "double_bottom",
            "ascending_triangle"
        ]
        
        for pattern_id in test_patterns:
            print(f"📊 Pattern: {pattern_id}")
            pattern = kb.get_pattern(pattern_id)
            if pattern:
                print(f"   - Source: {pattern.get('source')}")
                print(f"   - Category: {pattern.get('category')}")
                print(f"   - Signal: {pattern.get('signal')}")
                
                success_rate = kb.get_success_rate(pattern_id)
                if success_rate:
                    print(f"   - Success Rate: {success_rate}%")
                
                rank = kb.get_bulkowski_rank(pattern_id)
                if rank:
                    print(f"   - Bulkowski Rank: {rank}")
                
                trading = kb.get_trading_playbook(pattern_id)
                if trading and trading.get("entry_rules"):
                    print(f"   - Entry Rules: {len(trading['entry_rules'])} rules")
                
                print()
            else:
                print(f"   ❌ Not found\n")
        
        # Test high-success patterns
        print("📈 High Success Patterns (>70%):")
        high_success = kb.get_high_success_patterns(70.0)
        for pattern_id, rate in high_success[:10]:
            print(f"   - {pattern_id}: {rate}%")
        
        print(f"\n✅ Total high-success patterns: {len(high_success)}")
    else:
        print("❌ Failed to load knowledge base")

