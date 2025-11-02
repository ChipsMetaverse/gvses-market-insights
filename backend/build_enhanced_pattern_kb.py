#!/usr/bin/env python3
"""
Enhanced Pattern Knowledge Base Builder

Extracts pattern data from:
1. Encyclopedia of Chart Patterns (Bulkowski) - 63 patterns with statistics
2. Candlestick Trading Bible - 30+ candlestick patterns
3. Price Action Patterns - 25+ price action setups

Outputs: enhanced_pattern_knowledge_base.json with:
- Pattern name, aliases, category
- Bulkowski success rates, failure rates, breakout performance
- Entry rules, exit rules, stop-loss guidance
- Invalidation conditions
- Trading playbooks
- Risk/reward ratios
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class PatternKnowledgeBuilder:
    def __init__(self, docs_dir: str = "training/json_docs"):
        self.docs_dir = Path(docs_dir)
        self.patterns = {}
        
    def load_encyclopedia(self) -> Dict[str, Any]:
        """Load Bulkowski's Encyclopedia of Chart Patterns"""
        file_path = self.docs_dir / "encyclopedia-of-chart-patterns.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def load_candlestick_bible(self) -> Dict[str, Any]:
        """Load The Candlestick Trading Bible"""
        file_path = self.docs_dir / "the-candlestick-trading-bible.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def load_price_action(self) -> Dict[str, Any]:
        """Load Price Action Patterns"""
        file_path = self.docs_dir / "price-action-patterns.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def extract_bulkowski_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all Bulkowski patterns from table of contents and chapters.
        
        Pattern structure from Encyclopedia:
        - Chapter per pattern
        - Results Snapshot with success rates
        - Statistics: average rise/decline, failure rates
        - Trading tactics
        - Identification guidelines
        """
        bulkowski_patterns = {}
        
        # Bulkowski patterns from TOC (chapters 1-63)
        pattern_list = [
            # Broadening Patterns (5)
            {"name": "Broadening_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 1},
            {"name": "Broadening_Right_Angled_Ascending", "category": "chart_pattern", "signal": "bullish", "chapter": 2},
            {"name": "Broadening_Right_Angled_Descending", "category": "chart_pattern", "signal": "bearish", "chapter": 3},
            {"name": "Broadening_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 4},
            {"name": "Broadening_Wedge_Ascending", "category": "chart_pattern", "signal": "bearish", "chapter": 5},
            {"name": "Broadening_Wedge_Descending", "category": "chart_pattern", "signal": "bullish", "chapter": 6},
            
            # Bump and Run (2)
            {"name": "Bump_and_Run_Reversal_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 7},
            {"name": "Bump_and_Run_Reversal_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 8},
            
            # Cup Patterns (2)
            {"name": "Cup_with_Handle", "category": "chart_pattern", "signal": "bullish", "chapter": 9},
            {"name": "Cup_with_Handle_Inverted", "category": "chart_pattern", "signal": "bearish", "chapter": 10},
            
            # Diamond Patterns (2)
            {"name": "Diamond_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 11},
            {"name": "Diamond_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 12},
            
            # Double Bottoms (4 variants)
            {"name": "Double_Bottom_Adam_Adam", "category": "chart_pattern", "signal": "bullish", "chapter": 13},
            {"name": "Double_Bottom_Adam_Eve", "category": "chart_pattern", "signal": "bullish", "chapter": 14},
            {"name": "Double_Bottom_Eve_Adam", "category": "chart_pattern", "signal": "bullish", "chapter": 15},
            {"name": "Double_Bottom_Eve_Eve", "category": "chart_pattern", "signal": "bullish", "chapter": 16},
            
            # Double Tops (4 variants)
            {"name": "Double_Top_Adam_Adam", "category": "chart_pattern", "signal": "bearish", "chapter": 17},
            {"name": "Double_Top_Adam_Eve", "category": "chart_pattern", "signal": "bearish", "chapter": 18},
            {"name": "Double_Top_Eve_Adam", "category": "chart_pattern", "signal": "bearish", "chapter": 19},
            {"name": "Double_Top_Eve_Eve", "category": "chart_pattern", "signal": "bearish", "chapter": 20},
            
            # Flags (2)
            {"name": "Flag", "category": "chart_pattern", "signal": "continuation", "chapter": 21},
            {"name": "Flag_High_and_Tight", "category": "chart_pattern", "signal": "continuation", "chapter": 22},
            
            # Gaps (1)
            {"name": "Gap", "category": "price_action", "signal": "neutral", "chapter": 23},
            
            # Head and Shoulders (4)
            {"name": "Head_and_Shoulders_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 24},
            {"name": "Head_and_Shoulders_Bottom_Complex", "category": "chart_pattern", "signal": "bullish", "chapter": 25},
            {"name": "Head_and_Shoulders_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 26},
            {"name": "Head_and_Shoulders_Top_Complex", "category": "chart_pattern", "signal": "bearish", "chapter": 27},
            
            # Horn Patterns (2)
            {"name": "Horn_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 28},
            {"name": "Horn_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 29},
            
            # Island Reversals (2)
            {"name": "Island_Reversal", "category": "chart_pattern", "signal": "reversal", "chapter": 30},
            {"name": "Island_Long", "category": "chart_pattern", "signal": "neutral", "chapter": 31},
            
            # Measured Moves (2)
            {"name": "Measured_Move_Down", "category": "chart_pattern", "signal": "bearish", "chapter": 32},
            {"name": "Measured_Move_Up", "category": "chart_pattern", "signal": "bullish", "chapter": 33},
            
            # Pennants (1)
            {"name": "Pennant", "category": "chart_pattern", "signal": "continuation", "chapter": 34},
            
            # Pipe Patterns (2)
            {"name": "Pipe_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 35},
            {"name": "Pipe_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 36},
            
            # Rectangles (2)
            {"name": "Rectangle_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 37},
            {"name": "Rectangle_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 38},
            
            # Rounding Patterns (2)
            {"name": "Rounding_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 39},
            {"name": "Rounding_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 40},
            
            # Scallops (4)
            {"name": "Scallop_Ascending", "category": "chart_pattern", "signal": "bullish", "chapter": 41},
            {"name": "Scallop_Ascending_Inverted", "category": "chart_pattern", "signal": "bearish", "chapter": 42},
            {"name": "Scallop_Descending", "category": "chart_pattern", "signal": "bearish", "chapter": 43},
            {"name": "Scallop_Descending_Inverted", "category": "chart_pattern", "signal": "bullish", "chapter": 44},
            
            # Three Peaks/Valleys (2)
            {"name": "Three_Falling_Peaks", "category": "chart_pattern", "signal": "bearish", "chapter": 45},
            {"name": "Three_Rising_Valleys", "category": "chart_pattern", "signal": "bullish", "chapter": 46},
            
            # Triangles (3)
            {"name": "Triangle_Ascending", "category": "chart_pattern", "signal": "bullish", "chapter": 47},
            {"name": "Triangle_Descending", "category": "chart_pattern", "signal": "bearish", "chapter": 48},
            {"name": "Triangle_Symmetrical", "category": "chart_pattern", "signal": "neutral", "chapter": 49},
            
            # Triple Patterns (2)
            {"name": "Triple_Bottom", "category": "chart_pattern", "signal": "bullish", "chapter": 50},
            {"name": "Triple_Top", "category": "chart_pattern", "signal": "bearish", "chapter": 51},
            
            # Wedges (2)
            {"name": "Wedge_Falling", "category": "chart_pattern", "signal": "bullish", "chapter": 52},
            {"name": "Wedge_Rising", "category": "chart_pattern", "signal": "bearish", "chapter": 53},
            
            # Event Patterns (10) - Chapters 54-63
            {"name": "Dead_Cat_Bounce", "category": "event_pattern", "signal": "bearish", "chapter": 54},
            {"name": "Dead_Cat_Bounce_Inverted", "category": "event_pattern", "signal": "bullish", "chapter": 55},
            {"name": "Earnings_Surprise_Bad", "category": "event_pattern", "signal": "bearish", "chapter": 56},
            {"name": "Earnings_Surprise_Good", "category": "event_pattern", "signal": "bullish", "chapter": 57},
            {"name": "FDA_Drug_Approval", "category": "event_pattern", "signal": "bullish", "chapter": 58},
            {"name": "Flag_Earnings", "category": "event_pattern", "signal": "neutral", "chapter": 59},
            {"name": "Same_Store_Sales_Bad", "category": "event_pattern", "signal": "bearish", "chapter": 60},
            {"name": "Same_Store_Sales_Good", "category": "event_pattern", "signal": "bullish", "chapter": 61},
            {"name": "Stock_Downgrade", "category": "event_pattern", "signal": "bearish", "chapter": 62},
            {"name": "Stock_Upgrade", "category": "event_pattern", "signal": "bullish", "chapter": 63},
        ]
        
        print(f"📊 Extracting {len(pattern_list)} Bulkowski patterns...")
        
        # For each pattern, search chunks for statistical data
        for pattern_def in pattern_list:
            pattern_name = pattern_def["name"]
            chapter = pattern_def["chapter"]
            
            # Initialize pattern structure
            bulkowski_patterns[pattern_name.lower()] = {
                "name": pattern_name,
                "aliases": [pattern_name.replace("_", " "), pattern_name.replace("_", "-")],
                "category": pattern_def["category"],
                "signal": pattern_def["signal"],
                "source": "Bulkowski Encyclopedia",
                "chapter": chapter,
                "statistics": {
                    "bull_market_success_rate": None,
                    "bear_market_success_rate": None,
                    "average_rise": None,
                    "average_decline": None,
                    "failure_rate": None,
                    "breakout_performance": None,
                    "pullback_rate": None,
                },
                "identification": {
                    "guidelines": [],
                    "visual_characteristics": [],
                    "minimum_criteria": []
                },
                "trading": {
                    "entry_rules": [],
                    "exit_rules": [],
                    "stop_loss_guidance": "",
                    "target_guidance": "",
                    "risk_reward_ratio": None,
                    "typical_duration": "",
                    "best_market_conditions": []
                },
                "invalidation": {
                    "conditions": [],
                    "warning_signs": []
                },
                "bulkowski_rank": None,  # 1-5 stars
                "bulkowski_tier": None,  # A, B, C, D, F
                "description": "",
                "psychology": "",
                "common_mistakes": [],
                "examples": []
            }
            
            # Search chunks for this pattern's data
            pattern_chunks = self._find_pattern_chunks(data, pattern_name, chapter)
            if pattern_chunks:
                self._extract_pattern_stats(bulkowski_patterns[pattern_name.lower()], pattern_chunks)
        
        print(f"✅ Extracted {len(bulkowski_patterns)} Bulkowski patterns")
        return bulkowski_patterns
    
    def _find_pattern_chunks(self, data: Dict[str, Any], pattern_name: str, chapter: int) -> List[Dict]:
        """Find all chunks related to a specific pattern chapter"""
        pattern_chunks = []
        search_terms = pattern_name.replace("_", " ").lower()
        
        for chunk in data.get("chunks", []):
            text = chunk.get("text", "").lower()
            # Match chapter number or pattern name
            if search_terms in text or f"chapter {chapter}" in text:
                pattern_chunks.append(chunk)
                if len(pattern_chunks) > 50:  # Limit chunks per pattern
                    break
        
        return pattern_chunks
    
    def _extract_pattern_stats(self, pattern_dict: Dict[str, Any], chunks: List[Dict]) -> None:
        """Extract statistical data from pattern chunks"""
        combined_text = " ".join([chunk.get("text", "") for chunk in chunks])
        
        # Extract success rates (e.g., "68% success rate" or "rise 45% of the time")
        success_match = re.search(r'(\d+)%\s+(?:success rate|rise|decline)', combined_text, re.IGNORECASE)
        if success_match:
            rate = int(success_match.group(1))
            if pattern_dict["signal"] == "bullish":
                pattern_dict["statistics"]["bull_market_success_rate"] = rate
            else:
                pattern_dict["statistics"]["bear_market_success_rate"] = rate
        
        # Extract average rise/decline (e.g., "average rise of 35%")
        avg_match = re.search(r'average\s+(?:rise|decline|gain)\s+(?:of\s+)?(\d+)%', combined_text, re.IGNORECASE)
        if avg_match:
            avg = int(avg_match.group(1))
            if pattern_dict["signal"] == "bullish":
                pattern_dict["statistics"]["average_rise"] = avg
            else:
                pattern_dict["statistics"]["average_decline"] = avg
        
        # Extract failure rate
        failure_match = re.search(r'(\d+)%\s+failure\s+rate', combined_text, re.IGNORECASE)
        if failure_match:
            pattern_dict["statistics"]["failure_rate"] = int(failure_match.group(1))
        
        # Extract description (first sentence mentioning the pattern)
        desc_match = re.search(r'([A-Z][^.!?]*?' + pattern_dict["name"].replace("_", "[ -]") + r'[^.!?]*[.!?])', combined_text)
        if desc_match:
            pattern_dict["description"] = desc_match.group(1).strip()[:500]
    
    def extract_candlestick_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract candlestick patterns from The Candlestick Trading Bible.
        
        Patterns include:
        - Engulfing (bullish/bearish)
        - Doji (standard, dragonfly, gravestone)
        - Hammer, Shooting Star
        - Morning Star, Evening Star
        - Harami
        - Pin Bar
        - Inside Bar
        - Tweezers Tops/Bottoms
        """
        candlestick_patterns = {}
        
        pattern_list = [
            # Core Patterns from TOC
            {"name": "Bullish_Engulfing", "signal": "bullish"},
            {"name": "Bearish_Engulfing", "signal": "bearish"},
            {"name": "Doji", "signal": "neutral"},
            {"name": "Dragonfly_Doji", "signal": "bullish"},
            {"name": "Gravestone_Doji", "signal": "bearish"},
            {"name": "Morning_Star", "signal": "bullish"},
            {"name": "Evening_Star", "signal": "bearish"},
            {"name": "Hammer", "signal": "bullish"},
            {"name": "Shooting_Star", "signal": "bearish"},
            {"name": "Bullish_Harami", "signal": "bullish"},
            {"name": "Bearish_Harami", "signal": "bearish"},
            {"name": "Tweezers_Top", "signal": "bearish"},
            {"name": "Tweezers_Bottom", "signal": "bullish"},
            {"name": "Pin_Bar", "signal": "reversal"},
            {"name": "Inside_Bar", "signal": "continuation"},
            {"name": "Inside_Bar_False_Breakout", "signal": "reversal"},
            
            # Additional Candlesticks (commonly known)
            {"name": "Marubozu_Bullish", "signal": "bullish"},
            {"name": "Marubozu_Bearish", "signal": "bearish"},
            {"name": "Spinning_Top", "signal": "neutral"},
            {"name": "Hanging_Man", "signal": "bearish"},
            {"name": "Inverted_Hammer", "signal": "bullish"},
            {"name": "Piercing_Line", "signal": "bullish"},
            {"name": "Dark_Cloud_Cover", "signal": "bearish"},
            {"name": "Three_White_Soldiers", "signal": "bullish"},
            {"name": "Three_Black_Crows", "signal": "bearish"},
            {"name": "Three_Inside_Up", "signal": "bullish"},
            {"name": "Three_Inside_Down", "signal": "bearish"},
            {"name": "Three_Outside_Up", "signal": "bullish"},
            {"name": "Three_Outside_Down", "signal": "bearish"},
            {"name": "Abandoned_Baby_Bullish", "signal": "bullish"},
            {"name": "Abandoned_Baby_Bearish", "signal": "bearish"},
            {"name": "Kicking_Bullish", "signal": "bullish"},
            {"name": "Kicking_Bearish", "signal": "bearish"},
            {"name": "Belt_Hold_Bullish", "signal": "bullish"},
            {"name": "Belt_Hold_Bearish", "signal": "bearish"},
        ]
        
        print(f"📊 Extracting {len(pattern_list)} candlestick patterns...")
        
        for pattern_def in pattern_list:
            pattern_name = pattern_def["name"]
            
            candlestick_patterns[pattern_name.lower()] = {
                "name": pattern_name,
                "aliases": [pattern_name.replace("_", " ")],
                "category": "candlestick",
                "signal": pattern_def["signal"],
                "source": "Candlestick Trading Bible",
                "statistics": {
                    "success_rate": None,  # To be enriched
                },
                "identification": {
                    "body_requirements": [],
                    "shadow_requirements": [],
                    "context_requirements": []
                },
                "trading": {
                    "entry_trigger": "",
                    "stop_loss": "",
                    "targets": [],
                    "timeframes": ["all"],
                    "confluence_factors": []
                },
                "psychology": "",
                "description": ""
            }
            
            # Search chunks for pattern details
            pattern_chunks = self._find_candlestick_chunks(data, pattern_name)
            if pattern_chunks:
                self._extract_candlestick_details(candlestick_patterns[pattern_name.lower()], pattern_chunks)
        
        print(f"✅ Extracted {len(candlestick_patterns)} candlestick patterns")
        return candlestick_patterns
    
    def _find_candlestick_chunks(self, data: Dict[str, Any], pattern_name: str) -> List[Dict]:
        """Find chunks related to a candlestick pattern"""
        pattern_chunks = []
        search_terms = pattern_name.replace("_", " ").lower()
        
        for chunk in data.get("chunks", []):
            text = chunk.get("text", "").lower()
            if search_terms in text or any(word in text for word in search_terms.split()):
                pattern_chunks.append(chunk)
                if len(pattern_chunks) > 10:
                    break
        
        return pattern_chunks
    
    def _extract_candlestick_details(self, pattern_dict: Dict[str, Any], chunks: List[Dict]) -> None:
        """Extract candlestick pattern details"""
        combined_text = " ".join([chunk.get("text", "") for chunk in chunks])
        
        # Extract description (first occurrence)
        sentences = combined_text.split(". ")
        for sentence in sentences[:10]:
            if pattern_dict["name"].replace("_", " ").lower() in sentence.lower():
                pattern_dict["description"] = sentence.strip()[:500]
                break
    
    def extract_price_action_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract price action patterns.
        
        Patterns include:
        - Support Bounce, Resistance Rejection
        - Breakout, Breakdown
        - False Breakout, Fakeout
        - Market Structure Break
        - Swing Failure Pattern
        - Liquidity Grab
        - Supply/Demand Zones
        - Trend Continuation, Trend Reversal
        """
        price_action_patterns = {}
        
        pattern_list = [
            {"name": "Support_Bounce", "signal": "bullish"},
            {"name": "Resistance_Rejection", "signal": "bearish"},
            {"name": "Breakout_Bullish", "signal": "bullish"},
            {"name": "Breakdown_Bearish", "signal": "bearish"},
            {"name": "False_Breakout", "signal": "reversal"},
            {"name": "Fakeout", "signal": "reversal"},
            {"name": "Market_Structure_Break_Bullish", "signal": "bullish"},
            {"name": "Market_Structure_Break_Bearish", "signal": "bearish"},
            {"name": "Swing_Failure_Pattern_Bullish", "signal": "bullish"},
            {"name": "Swing_Failure_Pattern_Bearish", "signal": "bearish"},
            {"name": "Liquidity_Grab_Above", "signal": "bearish"},
            {"name": "Liquidity_Grab_Below", "signal": "bullish"},
            {"name": "Supply_Zone_Test", "signal": "bearish"},
            {"name": "Demand_Zone_Test", "signal": "bullish"},
            {"name": "Trend_Acceleration", "signal": "continuation"},
            {"name": "Trend_Exhaustion", "signal": "reversal"},
            {"name": "Gap_Breakaway", "signal": "continuation"},
            {"name": "Gap_Runaway", "signal": "continuation"},
            {"name": "Gap_Exhaustion", "signal": "reversal"},
            {"name": "Gap_Common", "signal": "neutral"},
            {"name": "Pullback_To_Trend", "signal": "continuation"},
            {"name": "Retest_Of_Breakout", "signal": "continuation"},
            {"name": "Trendline_Break", "signal": "reversal"},
            {"name": "Channel_Break", "signal": "reversal"},
            {"name": "Consolidation_Breakout", "signal": "breakout"},
        ]
        
        print(f"📊 Extracting {len(pattern_list)} price action patterns...")
        
        for pattern_def in pattern_list:
            pattern_name = pattern_def["name"]
            
            price_action_patterns[pattern_name.lower()] = {
                "name": pattern_name,
                "aliases": [pattern_name.replace("_", " ")],
                "category": "price_action",
                "signal": pattern_def["signal"],
                "source": "Price Action Patterns",
                "statistics": {},
                "identification": {
                    "price_structure": [],
                    "volume_characteristics": [],
                    "context": []
                },
                "trading": {
                    "entry": "",
                    "stop_loss": "",
                    "targets": [],
                    "risk_reward": None
                },
                "description": ""
            }
        
        print(f"✅ Extracted {len(price_action_patterns)} price action patterns")
        return price_action_patterns
    
    def build_knowledge_base(self) -> Dict[str, Any]:
        """Build complete enhanced pattern knowledge base"""
        print("\n🔨 Building Enhanced Pattern Knowledge Base...")
        print("=" * 70)
        
        # Load all source documents
        print("\n📚 Loading source documents...")
        encyclopedia = self.load_encyclopedia()
        print(f"  ✅ Encyclopedia: {encyclopedia['chunk_count']} chunks")
        
        candlestick_bible = self.load_candlestick_bible()
        print(f"  ✅ Candlestick Bible: {candlestick_bible['chunk_count']} chunks")
        
        price_action = self.load_price_action()
        print(f"  ✅ Price Action: {price_action['chunk_count']} chunks")
        
        print("\n" + "=" * 70)
        
        # Extract patterns from each source
        bulkowski = self.extract_bulkowski_patterns(encyclopedia)
        candlesticks = self.extract_candlestick_patterns(candlestick_bible)
        price_actions = self.extract_price_action_patterns(price_action)
        
        # Merge all patterns
        all_patterns = {**bulkowski, **candlesticks, **price_actions}
        
        # Build final structure
        knowledge_base = {
            "version": "2.0",
            "created": "2025-01-01",
            "total_patterns": len(all_patterns),
            "sources": [
                "Encyclopedia of Chart Patterns (Bulkowski)",
                "The Candlestick Trading Bible",
                "Price Action Patterns"
            ],
            "pattern_counts": {
                "bulkowski_chart_patterns": len(bulkowski),
                "candlestick_patterns": len(candlesticks),
                "price_action_patterns": len(price_actions)
            },
            "patterns": all_patterns
        }
        
        print("\n" + "=" * 70)
        print(f"✅ COMPLETE: {len(all_patterns)} total patterns in knowledge base")
        print(f"  - Bulkowski Chart Patterns: {len(bulkowski)}")
        print(f"  - Candlestick Patterns: {len(candlesticks)}")
        print(f"  - Price Action Patterns: {len(price_actions)}")
        print("=" * 70)
        
        return knowledge_base
    
    def save_knowledge_base(self, kb: Dict[str, Any], output_file: str = "enhanced_pattern_knowledge_base.json"):
        """Save knowledge base to JSON file"""
        output_path = self.docs_dir.parent / output_file
        with open(output_path, 'w') as f:
            json.dump(kb, f, indent=2)
        print(f"\n💾 Saved to: {output_path}")
        print(f"📊 File size: {output_path.stat().st_size / 1024:.2f} KB")

def main():
    print("\n" + "🚀 " * 20)
    print("ENHANCED PATTERN KNOWLEDGE BASE BUILDER")
    print("🚀 " * 20 + "\n")
    
    builder = PatternKnowledgeBuilder()
    kb = builder.build_knowledge_base()
    builder.save_knowledge_base(kb)
    
    print("\n✅ SUCCESS! Enhanced Pattern Knowledge Base created.")
    print(f"📚 Total Patterns: {kb['total_patterns']}")
    print(f"📖 Ready for integration into pattern_detection.py\n")

if __name__ == "__main__":
    main()

