"""
Simplified Intent Router for Voice Trading Assistant
Extracted from agent_orchestrator.py for cleaner architecture
"""

from typing import Dict, List, Optional
import re


class IntentRouter:
    """Routes user queries to appropriate handlers based on intent classification."""
    
    def __init__(self):
        self.intent_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent detection patterns."""
        return {
            "educational": [
                "what does", "what is", "how do i", "how to", "explain", 
                "what's the difference", "teach me", "trading basics", 
                "start trading", "beginner", "learn", "understand", 
                "meaning of", "definition"
            ],
            "price-only": [
                "price", "quote", "cost", "worth", "value", 
                "trading at", "how much is"
            ],
            "chart-only": [
                "show chart", "display chart", "load chart", "view chart",
                "show me the chart", "chart for", "chart of"
            ],
            "news": [
                "news", "headlines", "catalyst", "latest", 
                "breaking", "announcement"
            ],
            "technical": [
                "technical", "analysis", "pattern", "support", 
                "resistance", "trend", "swing", "entry", "exit"
            ],
            "trading-plan": [
                "what should i trade", "trading plan", "what to trade",
                "trade next week", "trade today", "trade tomorrow",
                "watchlist", "trading ideas", "trade recommendations"
            ],
            "company-info": [
                "what is", "who is", "tell me about", "explain"
            ]
        }
    
    def classify_intent(self, query: str) -> str:
        """
        Classify the intent of a user query.
        
        Args:
            query: User's input query (original case)
            
        Returns:
            Intent classification string
        """
        query_lower = query.lower()
        
        # Check company info queries FIRST (before educational)
        # "What is PLTR?" should be company-info, not educational
        # Pass original query for symbol extraction (needs uppercase)
        if self._is_company_info(query, query_lower):
            return "company-info"
        
        # Check educational queries (after company-info to avoid conflicts)
        if self._is_educational(query_lower):
            return "educational"
        
        # Price-only queries (simple and short)
        if self._is_price_query(query_lower):
            return "price-only"
        
        # Chart display commands
        if self._is_chart_request(query_lower):
            return "chart-only"
        
        # News queries
        if any(term in query_lower for term in self.intent_patterns["news"]):
            return "news"
        
        # Technical analysis
        if any(term in query_lower for term in self.intent_patterns["technical"]):
            return "technical"
        
        # Trading plan/watchlist
        if any(term in query_lower for term in self.intent_patterns["trading-plan"]):
            return "trading-plan"
        
        # Default to general query
        return "general"
    
    def _is_educational(self, query: str) -> bool:
        """Check if query is educational in nature."""
        return any(trigger in query for trigger in self.intent_patterns["educational"])
    
    def _is_price_query(self, query: str) -> bool:
        """Check if query is asking for price only."""
        has_price_term = any(term in query for term in self.intent_patterns["price-only"])
        is_short = len(query.split()) < 12
        no_complex_terms = not any(term in query for term in ["analysis", "technical", "news", "chart"])
        return has_price_term and is_short and no_complex_terms
    
    def _is_chart_request(self, query: str) -> bool:
        """Check if query is requesting a chart display."""
        return any(term in query for term in self.intent_patterns["chart-only"])
    
    def _is_company_info(self, query_original: str, query_lower: str) -> bool:
        """
        Check if query is asking for company information.
        
        Args:
            query_original: Original query with original case (for symbol extraction)
            query_lower: Lowercase query (for pattern matching)
        """
        has_info_trigger = any(p in query_lower for p in self.intent_patterns["company-info"])
        no_price_terms = not any(term in query_lower for term in ["price", "quote", "cost", "trading"])
        has_symbol = self.extract_symbol(query_original) is not None
        # Must have info trigger, no price terms, AND a stock symbol to be company-info
        return has_info_trigger and no_price_terms and has_symbol
    
    def extract_symbol(self, query: str) -> Optional[str]:
        """
        Extract stock symbol from query.
        
        Args:
            query: User's input query
            
        Returns:
            Stock symbol if found, None otherwise
        """
        # Look for uppercase symbols (2-5 characters)
        symbol_pattern = r'\b[A-Z]{2,5}\b'
        matches = re.findall(symbol_pattern, query)
        
        # Filter out common words that might match pattern
        common_words = {"THE", "AND", "FOR", "WITH", "FROM", "WHAT", "HOW", "WHY"}
        symbols = [m for m in matches if m not in common_words]
        
        return symbols[0] if symbols else None


# Export main class
__all__ = ['IntentRouter']