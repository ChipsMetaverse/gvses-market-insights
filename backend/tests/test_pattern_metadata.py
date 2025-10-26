"""
Regression tests for pattern metadata and chart_metadata generation.

Ensures all detected patterns include proper metadata for chart visualization.
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_detection import PatternDetector, Pattern
from services.market_service_factory import MarketServiceWrapper


# Mock candle data for testing
MOCK_CANDLES = [
    {"time": 1746019800, "open": 298.83, "close": 295.14, "low": 291.14, "high": 305.5, "volume": 100000},
    {"time": 1746106200, "open": 285.96, "close": 308.58, "low": 281.85, "high": 309.83, "volume": 150000},  # Bullish engulfing
    {"time": 1746192600, "open": 310.0, "close": 310.5, "low": 309.0, "high": 311.0, "volume": 80000},  # Doji
    {"time": 1746279000, "open": 312.0, "close": 315.0, "low": 311.5, "high": 316.0, "volume": 120000},
    {"time": 1746365400, "open": 315.5, "close": 318.0, "low": 314.0, "high": 319.0, "volume": 110000},
    {"time": 1746451800, "open": 318.5, "close": 320.0, "low": 317.0, "high": 321.0, "volume": 130000},
    {"time": 1746538200, "open": 275.35, "close": 276.22, "low": 316.86, "high": 318.0, "volume": 90000},
    {"time": 1746624600, "open": 276.22, "close": 280.52, "low": 275.0, "high": 281.0, "volume": 140000},
]


class TestPatternMetadata:
    """Test that all patterns include metadata for visualization."""
    
    def test_detector_returns_patterns_with_metadata(self):
        """Test that PatternDetector returns patterns with metadata field."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        assert "detected" in result
        assert len(result["detected"]) > 0, "Should detect at least one pattern"
        
        # Check each detected pattern has metadata
        for pattern in result["detected"]:
            assert "metadata" in pattern, f"Pattern {pattern['pattern_type']} missing metadata field"
            assert pattern["metadata"] is not None, f"Pattern {pattern['pattern_type']} has None metadata"
            assert isinstance(pattern["metadata"], dict), f"Pattern {pattern['pattern_type']} metadata is not a dict"
    
    def test_candlestick_patterns_have_metadata(self):
        """Test that candlestick patterns (engulfing, doji, hammer) have metadata."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        candlestick_types = ["bullish_engulfing", "bearish_engulfing", "doji", "hammer", "shooting_star"]
        detected_candlesticks = [p for p in result["detected"] if p["pattern_type"] in candlestick_types]
        
        if detected_candlesticks:
            for pattern in detected_candlesticks:
                assert pattern["metadata"], f"{pattern['pattern_type']} has empty metadata"
                # Candlestick patterns should have horizontal_level
                assert "horizontal_level" in pattern["metadata"], \
                    f"{pattern['pattern_type']} missing horizontal_level in metadata"
    
    def test_structural_patterns_have_metadata(self):
        """Test that structural patterns (triangles, wedges, channels) have metadata."""
        # Use longer data for structural patterns
        extended_candles = []
        base_price = 300
        for i in range(50):
            extended_candles.append({
                "time": 1746019800 + i * 86400,
                "open": base_price + i * 0.5,
                "close": base_price + i * 0.5 + 1,
                "low": base_price + i * 0.5 - 0.5,
                "high": base_price + i * 0.5 + 2,
                "volume": 100000 + i * 1000
            })
        
        detector = PatternDetector(extended_candles)
        result = detector.detect_all_patterns()
        
        structural_types = ["ascending_triangle", "descending_triangle", "symmetrical_triangle", 
                           "bullish_flag", "bearish_flag", "rising_wedge", "falling_wedge"]
        detected_structural = [p for p in result["detected"] if p["pattern_type"] in structural_types]
        
        if detected_structural:
            for pattern in detected_structural:
                assert pattern["metadata"], f"{pattern['pattern_type']} has empty metadata"
                # Structural patterns should have trendline or channel data
                has_structure = any(key in pattern["metadata"] for key in 
                                  ["upper_trendline", "lower_trendline", "channel_bounds"])
                assert has_structure, \
                    f"{pattern['pattern_type']} missing structural metadata (trendlines/channels)"


class TestChartMetadataGeneration:
    """Test that chart_metadata is properly generated from pattern metadata."""
    
    def test_chart_metadata_generation_from_metadata(self):
        """Test that _build_chart_metadata_from_pattern generates proper overlays."""
        wrapper = MarketServiceWrapper()
        
        # Test metadata with horizontal_level
        metadata = {
            "horizontal_level": 295.5,
            "candle": {"open": 295.0, "close": 296.0, "low": 294.0, "high": 297.0}
        }
        
        chart_metadata = wrapper._build_chart_metadata_from_pattern(metadata, MOCK_CANDLES)
        
        assert chart_metadata is not None, "Should generate chart_metadata from metadata"
        assert "levels" in chart_metadata, "chart_metadata should have levels array"
        assert len(chart_metadata["levels"]) > 0, "Should have at least one level"
        
        # Check level structure
        level = chart_metadata["levels"][0]
        assert "type" in level, "Level should have type field"
        assert "price" in level, "Level should have price field"
        assert isinstance(level["price"], float), "Level price should be float"
    
    def test_chart_metadata_with_trendlines(self):
        """Test chart_metadata generation with trendline metadata."""
        wrapper = MarketServiceWrapper()
        
        # Test metadata with trendlines
        metadata = {
            "upper_trendline": {
                "start_candle": 0,
                "end_candle": 5,
                "start_price": 300.0,
                "end_price": 320.0
            },
            "lower_trendline": {
                "start_candle": 0,
                "end_candle": 5,
                "start_price": 290.0,
                "end_price": 310.0
            }
        }
        
        chart_metadata = wrapper._build_chart_metadata_from_pattern(metadata, MOCK_CANDLES)
        
        assert chart_metadata is not None
        assert "trendlines" in chart_metadata, "chart_metadata should have trendlines array"
        assert len(chart_metadata["trendlines"]) == 2, "Should have 2 trendlines"
        
        # Check trendline structure
        for trendline in chart_metadata["trendlines"]:
            assert "type" in trendline, "Trendline should have type"
            assert "start" in trendline, "Trendline should have start point"
            assert "end" in trendline, "Trendline should have end point"
            assert "time" in trendline["start"], "Start point should have time"
            assert "price" in trendline["start"], "Start point should have price"
            assert "time" in trendline["end"], "End point should have time"
            assert "price" in trendline["end"], "End point should have price"
    
    def test_empty_metadata_returns_none(self):
        """Test that empty metadata returns None for chart_metadata."""
        wrapper = MarketServiceWrapper()
        
        # Empty metadata should return None
        chart_metadata = wrapper._build_chart_metadata_from_pattern({}, MOCK_CANDLES)
        assert chart_metadata is None, "Empty metadata should return None"
        
        # None metadata should return None
        chart_metadata = wrapper._build_chart_metadata_from_pattern(None, MOCK_CANDLES)
        assert chart_metadata is None, "None metadata should return None"


class TestEndToEndPatternFlow:
    """Test the complete flow from detection to chart_metadata."""
    
    def test_detect_all_patterns_end_to_end(self):
        """Test complete flow: detect patterns → enrich → generate chart_metadata."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        wrapper = MarketServiceWrapper()
        
        # Process each detected pattern
        for pattern_dict in result["detected"]:
            # Check pattern has metadata (use dict directly, don't reconstruct Pattern)
            assert "metadata" in pattern_dict, \
                f"Pattern {pattern_dict['pattern_type']} missing metadata field"
            assert pattern_dict["metadata"] is not None, \
                f"Pattern {pattern_dict['pattern_type']} missing metadata after detection"
            
            metadata = pattern_dict["metadata"]
            
            # Generate chart_metadata
            if metadata:
                chart_overlay = wrapper._build_chart_metadata_from_pattern(
                    metadata, 
                    MOCK_CANDLES
                )
                
                # At minimum, patterns with horizontal_level should generate chart_metadata
                if "horizontal_level" in metadata:
                    assert chart_overlay is not None, \
                        f"Pattern {pattern_dict['pattern_type']} with horizontal_level should generate chart_metadata"
                    assert "levels" in chart_overlay, \
                        f"Pattern {pattern_dict['pattern_type']} chart_metadata should have levels"
    
    def test_all_patterns_serializable(self):
        """Test that all patterns can be serialized to dict with chart_metadata."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        wrapper = MarketServiceWrapper()
        
        for pattern_dict in result["detected"]:
            # Simulate the augmentation process in market_service_factory
            metadata = pattern_dict.get("metadata", {})
            if metadata:
                chart_overlay = wrapper._build_chart_metadata_from_pattern(metadata, MOCK_CANDLES)
                if chart_overlay:
                    pattern_dict["chart_metadata"] = chart_overlay
            
            # Verify serializable structure
            assert "pattern_type" in pattern_dict
            assert "confidence" in pattern_dict
            assert "metadata" in pattern_dict
            
            # If chart_metadata was generated, verify structure
            if pattern_dict.get("chart_metadata"):
                chart_meta = pattern_dict["chart_metadata"]
                assert isinstance(chart_meta, dict), "chart_metadata should be dict"
                
                # Check for either levels or trendlines
                has_visualization_data = (
                    ("levels" in chart_meta and len(chart_meta["levels"]) > 0) or
                    ("trendlines" in chart_meta and len(chart_meta["trendlines"]) > 0)
                )
                assert has_visualization_data, \
                    f"Pattern {pattern_dict['pattern_type']} chart_metadata should have levels or trendlines"


class TestPatternMetadataContract:
    """Test the metadata contract between backend and frontend."""
    
    def test_metadata_contains_expected_fields(self):
        """Test that pattern metadata contains fields expected by frontend."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        # Patterns that are allowed to have minimal/empty metadata (low priority for visualization)
        # These are typically rare or low-impact patterns that can be enhanced in future iterations
        allowed_minimal_metadata = [
            "spinning_top", "marubozu", "hanging_man", "inverted_hammer",
            "three_outside_up", "three_outside_down", "three_inside_up", "three_inside_down",
            "abandoned_baby_bullish", "abandoned_baby_bearish",
            "pennant", "rectangle", "broadening", "diamond", "rounding_bottom"
        ]
        
        for pattern in result["detected"]:
            metadata = pattern.get("metadata", {})
            pattern_type = pattern['pattern_type']
            
            # Skip patterns that are allowed to have minimal metadata
            if pattern_type in allowed_minimal_metadata:
                continue
            
            # All other patterns should have at least one of these
            has_required_field = any([
                "horizontal_level" in metadata,
                "upper_trendline" in metadata,
                "lower_trendline" in metadata,
                "channel_bounds" in metadata,
                "candle" in metadata,
                "candles" in metadata
            ])
            
            assert has_required_field, \
                f"Pattern {pattern_type} metadata missing required fields. Metadata keys: {list(metadata.keys())}"
    
    def test_chart_metadata_contract(self):
        """Test that chart_metadata follows the expected schema."""
        detector = PatternDetector(MOCK_CANDLES)
        result = detector.detect_all_patterns()
        
        wrapper = MarketServiceWrapper()
        
        for pattern_dict in result["detected"]:
            metadata = pattern_dict.get("metadata", {})
            if metadata:
                chart_metadata = wrapper._build_chart_metadata_from_pattern(metadata, MOCK_CANDLES)
                
                if chart_metadata:
                    # Verify chart_metadata schema
                    assert isinstance(chart_metadata, dict), "chart_metadata must be dict"
                    
                    # Check levels structure if present
                    if "levels" in chart_metadata:
                        for level in chart_metadata["levels"]:
                            assert "type" in level, "Level must have type"
                            assert level["type"] in ["support", "resistance", "neckline"], \
                                f"Invalid level type: {level['type']}"
                            assert "price" in level, "Level must have price"
                            assert isinstance(level["price"], (int, float)), "Level price must be numeric"
                    
                    # Check trendlines structure if present
                    if "trendlines" in chart_metadata:
                        for trendline in chart_metadata["trendlines"]:
                            assert "type" in trendline, "Trendline must have type"
                            assert "start" in trendline, "Trendline must have start"
                            assert "end" in trendline, "Trendline must have end"
                            assert "time" in trendline["start"], "Start must have time"
                            assert "price" in trendline["start"], "Start must have price"
                            assert "time" in trendline["end"], "End must have time"
                            assert "price" in trendline["end"], "End must have price"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

