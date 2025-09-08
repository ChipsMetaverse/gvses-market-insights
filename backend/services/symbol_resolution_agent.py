"""
Symbol Resolution Agent using OpenAI Agents SDK
Intelligent symbol resolution with priority rules for solving the google → GOOP bug
"""

import os
import logging
from typing import Optional, Dict, Any, List
from agents import Agent, Runner, function_tool
from services.market_service_factory import MarketServiceFactory

logger = logging.getLogger(__name__)

# Static mappings for common companies (prioritized over API search)
STATIC_COMPANY_MAPPINGS = {
    # Tech Giants
    'google': 'GOOGL',
    'alphabet': 'GOOGL',
    'microsoft': 'MSFT',
    'apple': 'AAPL', 
    'amazon': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'tesla': 'TSLA',
    'nvidia': 'NVDA',
    'netflix': 'NFLX',
    
    # Financial 
    'jpmorgan': 'JPM',
    'jp morgan': 'JPM',
    'chase': 'JPM',
    'bank of america': 'BAC',
    'wells fargo': 'WFC',
    'goldman': 'GS',
    'goldman sachs': 'GS',
    'berkshire': 'BRK.B',
    'berkshire hathaway': 'BRK.B',
    
    # Crypto (for voice commands)
    'bitcoin': 'BTC-USD',
    'ethereum': 'ETH-USD',
    'btc': 'BTC-USD',
    'eth': 'ETH-USD'
}

@function_tool
def check_static_mapping(company_name: str) -> dict:
    """Check if company has a predefined ticker mapping."""
    company_lower = company_name.lower().strip()
    
    if company_lower in STATIC_COMPANY_MAPPINGS:
        ticker = STATIC_COMPANY_MAPPINGS[company_lower]
        asset_type = 'crypto' if ticker.endswith('-USD') else 'stock'
        
        return {
            "found": True,
            "symbol": ticker,
            "company_name": company_name.title(),
            "asset_type": asset_type,
            "source": "static_mapping",
            "priority": "high"
        }
    
    return {
        "found": False,
        "reason": f"No static mapping found for '{company_name}'"
    }

@function_tool
async def search_alpaca_symbols(query: str, limit: int = 5) -> dict:
    """Search for symbols using Alpaca API with stock prioritization."""
    try:
        service = MarketServiceFactory.get_service()
        if not service:
            return {
                "found": False,
                "error": "Market service not available"
            }
        
        # Search via Alpaca API
        results = await service.search_assets(query, limit)
        
        if not results:
            return {
                "found": False,
                "reason": f"No symbols found for '{query}'"
            }
        
        # Prioritize actual stocks over ETFs
        stock_results = []
        etf_results = []
        
        for result in results:
            # Check if it's likely an ETF (common ETF patterns)
            symbol = result.get('symbol', '')
            name = result.get('name', '').lower()
            
            is_etf = (
                'etf' in name or 
                'fund' in name or
                'index' in name or
                'trust' in name or
                symbol in ['SPY', 'QQQ', 'DIA', 'VTI', 'VOO', 'GOOP']  # Known ETFs
            )
            
            if is_etf:
                etf_results.append(result)
            else:
                stock_results.append(result)
        
        # Prioritize stocks, then ETFs
        prioritized_results = stock_results + etf_results
        
        if prioritized_results:
            best_match = prioritized_results[0]
            return {
                "found": True,
                "symbol": best_match.get('symbol'),
                "company_name": best_match.get('name'),
                "asset_type": "stock",
                "source": "alpaca_api",
                "priority": "medium",
                "all_results": prioritized_results[:3]  # Include alternatives
            }
        
        return {
            "found": False,
            "reason": f"No suitable symbols found for '{query}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching Alpaca symbols for '{query}': {e}")
        return {
            "found": False,
            "error": str(e)
        }

@function_tool 
def validate_symbol_format(symbol: str) -> dict:
    """Validate if a string looks like a valid stock symbol."""
    if not symbol or len(symbol) < 1:
        return {"valid": False, "reason": "Symbol cannot be empty"}
    
    symbol_upper = symbol.upper()
    
    # Valid patterns:
    # Stock: 1-5 uppercase letters (AAPL, MSFT, GOOGL)
    # Crypto: XXX-USD, XXX-USDT, etc (BTC-USD, ETH-USD) 
    # Special: BRK.A, BRK.B (Berkshire classes)
    import re
    
    stock_pattern = re.match(r'^[A-Z]{1,5}$', symbol_upper)
    crypto_pattern = re.match(r'^[A-Z]{2,5}-(USD|USDT|USDC|EUR|BTC|ETH)$', symbol_upper)
    berkshire_pattern = re.match(r'^BRK\.[AB]$', symbol_upper)
    
    if stock_pattern or crypto_pattern or berkshire_pattern:
        asset_type = 'crypto' if crypto_pattern else 'stock'
        return {
            "valid": True,
            "symbol": symbol_upper,
            "asset_type": asset_type
        }
    
    return {
        "valid": False,
        "reason": f"'{symbol}' doesn't match valid symbol format"
    }

class SymbolResolutionAgent:
    """Orchestrates intelligent symbol resolution using OpenAI Agents"""
    
    def __init__(self):
        """Initialize the symbol resolution agent system"""
        self.initialize_agents()
        self.runner = Runner()
        
    def initialize_agents(self):
        """Set up the agent architecture"""
        
        # Static mapping agent (highest priority)
        self.static_mapping_agent = Agent(
            name='Static Mapping Agent',
            handoff_description='Checks predefined company-to-ticker mappings first',
            instructions='''You check static company name mappings.
            Use the check_static_mapping tool to see if a company has a predefined ticker.
            If found, return that result immediately as it has highest priority.
            This prevents issues like Google→GOOP by ensuring Google→GOOGL.''',
            model='gpt-3.5-turbo',
            tools=[check_static_mapping]
        )
        
        # Alpaca search agent (medium priority, with stock prioritization)
        self.alpaca_search_agent = Agent(
            name='Alpaca Search Agent',
            handoff_description='Searches Alpaca API and prioritizes actual stocks over ETFs',
            instructions='''You search for symbols using the Alpaca Markets API.
            Use search_alpaca_symbols to find matches.
            The tool automatically prioritizes actual company stocks over ETFs.
            This ensures "google" returns GOOGL (Alphabet stock) not GOOP (Google ETF).
            Return the best match with company name and asset type.''',
            model='gpt-3.5-turbo', 
            tools=[search_alpaca_symbols]
        )
        
        # Validation agent (for format checking)
        self.validation_agent = Agent(
            name='Symbol Validation Agent',
            handoff_description='Validates symbol format and asset type',
            instructions='''You validate symbol formats using validate_symbol_format.
            Check if strings look like valid ticker symbols.
            Distinguish between stocks (AAPL) and crypto (BTC-USD).''',
            model='gpt-3.5-turbo',
            tools=[validate_symbol_format]
        )
        
        # Main orchestrator agent
        self.main_agent = Agent(
            name='Symbol Resolution Agent',
            instructions='''You resolve company names and queries to correct stock tickers.
            
            PRIORITY RULES:
            1. ALWAYS check static mappings first (highest priority)
            2. If no static mapping, use Alpaca search (prioritizes stocks over ETFs) 
            3. Validate final symbol format
            4. CRITICAL: For "google" return GOOGL not GOOP
            
            WORKFLOW:
            1. Hand off to Static Mapping Agent first
            2. If not found, hand off to Alpaca Search Agent  
            3. Validate result with Symbol Validation Agent
            4. Return the best match with source attribution
            
            Always prefer actual company stocks over ETFs or funds.''',
            model='gpt-3.5-turbo',
            handoffs=[self.static_mapping_agent, self.alpaca_search_agent, self.validation_agent]
        )
    
    async def resolve_symbol(self, query: str) -> Dict[str, Any]:
        """Resolve a company name or symbol query to the correct ticker"""
        try:
            logger.info(f"Resolving symbol for query: '{query}'")
            
            # Try fallback logic first (works without OpenAI API)
            fallback_result = await self.resolve_symbol_fallback(query)
            if fallback_result["success"]:
                logger.info(f"Fallback resolution successful for '{query}': {fallback_result['symbol']}")
                return fallback_result
            
            # Only try agent workflow if fallback fails and we have API key
            if os.getenv('OPENAI_API_KEY'):
                logger.info(f"Attempting agent workflow for '{query}'")
                result = await self.runner.run(
                    self.main_agent,
                    f"Resolve this to a stock ticker symbol: {query}",
                    context={"original_query": query}
                )
                
                # Parse agent result
                if hasattr(result, 'final_output'):
                    output = result.final_output
                    logger.info(f"Agent output for '{query}': {output}")
                    return {
                        "success": True,
                        "query": query,
                        "agent_output": output,
                        "workflow_complete": True
                    }
            else:
                logger.warning(f"No OpenAI API key available, using fallback result for '{query}'")
                return fallback_result
            
            return {
                "success": False,
                "query": query,
                "error": "No resolution method succeeded",
                "fallback_attempted": True
            }
            
        except Exception as e:
            logger.error(f"Error in symbol resolution for '{query}': {e}")
            # Return fallback attempt on error
            try:
                fallback_result = await self.resolve_symbol_fallback(query)
                fallback_result["note"] = f"Used fallback due to error: {str(e)}"
                return fallback_result
            except:
                return {
                    "success": False,
                    "query": query,
                    "error": str(e)
                }
    
    async def resolve_symbol_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback resolution using static mapping + Alpaca search (no OpenAI API required)"""
        query_clean = query.strip().lower()
        
        # Step 1: Check static mapping first (highest priority)
        if query_clean in STATIC_COMPANY_MAPPINGS:
            ticker = STATIC_COMPANY_MAPPINGS[query_clean]
            asset_type = 'crypto' if ticker.endswith('-USD') else 'stock'
            logger.info(f"Static mapping found: '{query}' → {ticker}")
            return {
                "success": True,
                "query": query,
                "symbol": ticker,
                "company_name": query.title(),
                "asset_type": asset_type,
                "source": "static_mapping",
                "confidence": 1.0,
                "method": "fallback"
            }
        
        # Step 2: Try Alpaca search if available
        try:
            service = MarketServiceFactory.get_service()
            if service:
                results = await service.search_assets(query, 3)
                if results:
                    # Prioritize stocks over ETFs
                    stock_results = []
                    etf_results = []
                    
                    for result in results:
                        symbol = result.get('symbol', '')
                        name = result.get('name', '').lower()
                        
                        is_etf = (
                            'etf' in name or 'fund' in name or 'index' in name or 
                            'trust' in name or symbol in ['SPY', 'QQQ', 'DIA', 'VTI', 'VOO', 'GOOP']
                        )
                        
                        if is_etf:
                            etf_results.append(result)
                        else:
                            stock_results.append(result)
                    
                    # Use stocks first, then ETFs
                    prioritized_results = stock_results + etf_results
                    if prioritized_results:
                        best_match = prioritized_results[0]
                        logger.info(f"Alpaca search found: '{query}' → {best_match.get('symbol')}")
                        return {
                            "success": True,
                            "query": query,
                            "symbol": best_match.get('symbol'),
                            "company_name": best_match.get('name'),
                            "asset_type": "stock",
                            "source": "alpaca_search",
                            "confidence": 0.8,
                            "method": "fallback",
                            "alternatives": [r.get('symbol') for r in prioritized_results[1:3]]
                        }
        except Exception as e:
            logger.warning(f"Alpaca search failed for '{query}': {e}")
        
        # Step 3: Check if it's already a valid symbol format
        symbol_upper = query.upper().strip()
        import re
        if re.match(r'^[A-Z]{1,5}$', symbol_upper) or re.match(r'^[A-Z]{2,5}-(USD|USDT|USDC)$', symbol_upper):
            logger.info(f"Query appears to be valid symbol: '{query}' → {symbol_upper}")
            return {
                "success": True,
                "query": query,
                "symbol": symbol_upper,
                "company_name": symbol_upper,
                "asset_type": "crypto" if "-" in symbol_upper else "stock",
                "source": "symbol_format",
                "confidence": 0.6,
                "method": "fallback"
            }
        
        # Step 4: No resolution found
        logger.warning(f"No fallback resolution found for '{query}'")
        return {
            "success": False,
            "query": query,
            "error": f"No resolution found for '{query}'",
            "method": "fallback",
            "attempted": ["static_mapping", "alpaca_search", "symbol_format"]
        }

    async def test_workflow(self) -> Dict[str, Any]:
        """Test the symbol resolution workflow with known cases"""
        test_cases = [
            "google",
            "microsoft", 
            "apple",
            "tesla",
            "MSFT",  # Direct ticker
            "alphabet"
        ]
        
        results = {}
        for query in test_cases:
            results[query] = await self.resolve_symbol(query)
        
        return {
            "test_results": results,
            "summary": f"Tested {len(test_cases)} cases"
        }

# Singleton instance
_symbol_resolution_agent = None

async def get_symbol_resolution_agent() -> SymbolResolutionAgent:
    """Get or create the symbol resolution agent singleton"""
    global _symbol_resolution_agent
    if _symbol_resolution_agent is None:
        _symbol_resolution_agent = SymbolResolutionAgent()
    return _symbol_resolution_agent

# Quick resolution function for immediate use
async def resolve_symbol_quick(query: str) -> Dict[str, Any]:
    """Quick symbol resolution - works without OpenAI API"""
    agent = await get_symbol_resolution_agent()
    return await agent.resolve_symbol_fallback(query)