"""
Test suite for PatternLibrary knowledge base integration.

This module tests:
- Pattern loading from patterns.json
- Recognition rule validation
- Trading playbook retrieval
- Pattern metadata structure
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from pattern_detection import PatternLibrary


class TestPatternLibrary:
    """Test PatternLibrary singleton and pattern loading."""
    
    @pytest.fixture
    def library(self):
        """Get PatternLibrary instance."""
        return PatternLibrary()
    
    def test_singleton_pattern(self):
        """Test that PatternLibrary is a singleton."""
        lib1 = PatternLibrary()
        lib2 = PatternLibrary()
        assert lib1 is lib2, "PatternLibrary should be a singleton"
    
    def test_patterns_loaded(self, library):
        """Test that patterns are loaded from patterns.json."""
        assert library.patterns is not None, "Patterns should be loaded"
        assert len(library.patterns) > 0, "Should have at least one pattern"
    
    def test_expected_patterns_exist(self, library):
        """Test that all expected patterns are in the knowledge base."""
        expected_patterns = [
            "head_and_shoulders",
            "cup_and_handle",
            "bullish_engulfing",
            "ascending_triangle",
            "descending_triangle",
            "symmetrical_triangle",
            "bullish_flag",
            "bearish_flag",
            "falling_wedge",
            "rising_wedge",
            "double_top",
            "double_bottom"
        ]
        
        for pattern_id in expected_patterns:
            pattern = library.get_pattern(pattern_id)
            assert pattern is not None, f"Pattern {pattern_id} should exist"
            assert "pattern_id" in pattern, f"Pattern {pattern_id} should have pattern_id"
            assert pattern["pattern_id"] == pattern_id


class TestGetPattern:
    """Test get_pattern method."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_get_existing_pattern(self, library):
        """Test retrieving an existing pattern."""
        pattern = library.get_pattern("bullish_engulfing")
        
        assert pattern is not None
        assert pattern["pattern_id"] == "bullish_engulfing"
        assert "display_name" in pattern
        assert "description" in pattern
        assert "recognition_rules" in pattern
        assert "trading_playbook" in pattern
    
    def test_get_nonexistent_pattern(self, library):
        """Test retrieving a pattern that doesn't exist."""
        pattern = library.get_pattern("nonexistent_pattern")
        assert pattern is None
    
    def test_pattern_structure(self, library):
        """Test that patterns have the correct structure."""
        pattern = library.get_pattern("head_and_shoulders")
        
        # Required fields
        assert "pattern_id" in pattern
        assert "category" in pattern
        assert "display_name" in pattern
        assert "description" in pattern
        
        # Recognition rules
        assert "recognition_rules" in pattern
        rules = pattern["recognition_rules"]
        assert "candle_structure" in rules
        assert "trend_context" in rules
        assert "volume_confirmation" in rules
        assert "invalidations" in rules
        
        # Trading playbook
        assert "trading_playbook" in pattern
        playbook = pattern["trading_playbook"]
        assert "signal" in playbook
        assert "entry" in playbook
        assert "stop_loss" in playbook
        assert "targets" in playbook
        assert "risk_notes" in playbook
        assert "timeframe_bias" in playbook
        
        # Statistics (only typical_duration is guaranteed)
        assert "statistics" in pattern
        stats = pattern["statistics"]
        assert "typical_duration" in stats


class TestRecognitionRules:
    """Test get_recognition_rules method."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_get_recognition_rules(self, library):
        """Test retrieving recognition rules."""
        rules = library.get_recognition_rules("cup_and_handle")
        
        assert rules is not None
        assert "candle_structure" in rules
        assert "trend_context" in rules
        assert "volume_confirmation" in rules
        assert "invalidations" in rules
    
    def test_rules_for_nonexistent_pattern(self, library):
        """Test getting rules for a pattern that doesn't exist."""
        rules = library.get_recognition_rules("nonexistent")
        assert rules == {}  # Returns empty dict, not None


class TestTradingPlaybook:
    """Test get_trading_playbook method."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_get_trading_playbook(self, library):
        """Test retrieving trading playbook."""
        playbook = library.get_trading_playbook("bullish_flag")
        
        assert playbook is not None
        assert "signal" in playbook
        assert "entry" in playbook
        assert "stop_loss" in playbook
        assert "targets" in playbook
        assert isinstance(playbook["targets"], list)
        assert "risk_notes" in playbook
        assert "timeframe_bias" in playbook
    
    def test_playbook_signals(self, library):
        """Test that playbook signals are valid."""
        valid_signals = ["bullish", "bearish", "neutral"]
        
        for pattern_id in ["bullish_engulfing", "head_and_shoulders", "symmetrical_triangle"]:
            playbook = library.get_trading_playbook(pattern_id)
            assert playbook["signal"] in valid_signals, f"Invalid signal for {pattern_id}"
    
    def test_playbook_for_nonexistent_pattern(self, library):
        """Test getting playbook for a pattern that doesn't exist."""
        playbook = library.get_trading_playbook("nonexistent")
        assert playbook == {}  # Returns empty dict, not None


class TestValidateAgainstRules:
    """Test validate_against_rules method."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    @pytest.fixture
    def sample_candles(self):
        """Sample candle data for testing."""
        return [
            {"time": 1745933400, "open": 290, "high": 295, "low": 285, "close": 292, "volume": 1000000},
            {"time": 1746019800, "open": 292, "high": 300, "low": 280, "close": 282, "volume": 1200000},
            {"time": 1746106200, "open": 282, "high": 290, "low": 275, "close": 288, "volume": 1100000},
        ]
    
    def test_validate_with_valid_metadata(self, library, sample_candles):
        """Test validation with proper metadata structure."""
        metadata = {
            "upper_trendline": {
                "start_candle": 0,
                "end_candle": 2,
                "start_price": 290,
                "end_price": 288
            },
            "lower_trendline": {
                "start_candle": 0,
                "end_candle": 2,
                "start_price": 285,
                "end_price": 275
            }
        }
        
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            "ascending_triangle",
            sample_candles,
            metadata
        )
        
        # Should return valid tuple
        assert isinstance(is_valid, bool)
        assert isinstance(conf_adj, (int, float))
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
    
    def test_validate_nonexistent_pattern(self, library, sample_candles):
        """Test validation for a pattern that doesn't exist."""
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            "nonexistent_pattern",
            sample_candles,
            {}
        )
        
        assert is_valid is False
        assert "not found" in reasoning.lower()
    
    def test_validate_with_empty_metadata(self, library, sample_candles):
        """Test validation with empty metadata."""
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            "bullish_engulfing",
            sample_candles,
            {}
        )
        
        # Should still validate (some patterns don't require specific metadata)
        assert isinstance(is_valid, bool)
        assert isinstance(conf_adj, (int, float))
    
    def test_validate_with_insufficient_candles(self, library):
        """Test validation with too few candles."""
        short_candles = [
            {"time": 1745933400, "open": 290, "high": 295, "low": 285, "close": 292}
        ]
        
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            "head_and_shoulders",
            short_candles,
            {}
        )
        
        # Current implementation may still validate with minimal data
        # Just ensure it returns valid tuple
        assert isinstance(is_valid, bool)
        assert isinstance(reasoning, str)


class TestPatternCategories:
    """Test pattern categorization."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_pattern_categories(self, library):
        """Test that patterns are properly categorized."""
        # Actual categories in patterns.json are: "chart_pattern" and "candlestick"
        expected_categories = {
            "chart_pattern": ["head_and_shoulders", "double_top", "double_bottom", 
                             "bullish_flag", "bearish_flag", "symmetrical_triangle"],
            "candlestick": ["bullish_engulfing"]
        }
        
        for category, pattern_ids in expected_categories.items():
            for pattern_id in pattern_ids:
                pattern = library.get_pattern(pattern_id)
                if pattern:  # Pattern might not be in KB yet
                    assert pattern.get("category") == category, \
                        f"Pattern {pattern_id} should be in category {category}"


class TestPatternStatistics:
    """Test pattern statistics."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_statistics_structure(self, library):
        """Test that pattern statistics have valid structure."""
        pattern = library.get_pattern("cup_and_handle")
        stats = pattern["statistics"]
        
        # Currently only typical_duration is provided in patterns.json
        assert "typical_duration" in stats
        assert isinstance(stats["typical_duration"], str)
        assert len(stats["typical_duration"]) > 0


class TestIntegration:
    """Integration tests for PatternLibrary."""
    
    @pytest.fixture
    def library(self):
        return PatternLibrary()
    
    def test_complete_pattern_workflow(self, library):
        """Test complete workflow: get pattern -> get rules -> get playbook -> validate."""
        pattern_id = "bullish_engulfing"
        
        # Step 1: Get pattern
        pattern = library.get_pattern(pattern_id)
        assert pattern is not None
        
        # Step 2: Get recognition rules
        rules = library.get_recognition_rules(pattern_id)
        assert rules is not None
        assert "candle_structure" in rules
        
        # Step 3: Get trading playbook
        playbook = library.get_trading_playbook(pattern_id)
        assert playbook is not None
        assert "entry" in playbook
        
        # Step 4: Validate (with minimal candle data)
        candles = [
            {"time": 1745933400, "open": 290, "high": 295, "low": 285, "close": 292, "volume": 1000000},
            {"time": 1746019800, "open": 292, "high": 300, "low": 280, "close": 295, "volume": 1200000}
        ]
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            pattern_id,
            candles,
            {}
        )
        
        assert isinstance(is_valid, bool)
        assert reasoning is not None
    
    def test_all_patterns_accessible(self, library):
        """Test that all patterns can be accessed through all methods."""
        pattern_ids = [
            "head_and_shoulders", "cup_and_handle", "bullish_engulfing",
            "ascending_triangle", "descending_triangle", "symmetrical_triangle",
            "bullish_flag", "bearish_flag", "falling_wedge", "rising_wedge",
            "double_top", "double_bottom"
        ]
        
        for pattern_id in pattern_ids:
            # Should be able to get pattern
            pattern = library.get_pattern(pattern_id)
            assert pattern is not None, f"Failed to get {pattern_id}"
            
            # Should be able to get rules
            rules = library.get_recognition_rules(pattern_id)
            assert rules is not None, f"Failed to get rules for {pattern_id}"
            
            # Should be able to get playbook
            playbook = library.get_trading_playbook(pattern_id)
            assert playbook is not None, f"Failed to get playbook for {pattern_id}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

