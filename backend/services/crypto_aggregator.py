"""
Crypto Aggregator Service
Aggregates cryptocurrency search results from multiple sources (Alpaca + CoinGecko)
"""

import logging
from typing import List, Dict, Any
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')


class CryptoAggregatorService:
    """Aggregate crypto search results from Alpaca (primary) and CoinGecko (fallback)."""

    def __init__(self, alpaca_service):
        """Initialize with reference to Alpaca service."""
        self.alpaca_service = alpaca_service

    async def search_all_crypto(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search crypto across Alpaca + CoinGecko with deduplication.

        Args:
            query: Search term (symbol or coin name)
            limit: Maximum total results to return

        Returns:
            List of crypto search results with source attribution
        """
        alpaca_results = []
        coingecko_results = []

        # Try Alpaca first (faster, professional-grade)
        try:
            if self.alpaca_service and self.alpaca_service.is_available:
                alpaca_results = await self.alpaca_service.search_crypto_assets(query, limit)
                logger.info(f"Alpaca crypto search returned {len(alpaca_results)} results")
        except Exception as e:
            logger.warning(f"Alpaca crypto search failed: {e}")

        # Fill gaps with CoinGecko if needed
        if len(alpaca_results) < limit:
            remaining = limit - len(alpaca_results)
            try:
                coingecko_results = await self._search_coingecko(query, remaining)
                logger.info(f"CoinGecko search returned {len(coingecko_results)} results")
            except Exception as e:
                logger.warning(f"CoinGecko search failed: {e}")

        # Merge and deduplicate
        merged_results = self._merge_crypto_results(alpaca_results, coingecko_results, limit)
        logger.info(f"Total aggregated crypto results: {len(merged_results)}")
        return merged_results

    async def _search_coingecko(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search CoinGecko API for crypto.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of formatted crypto results
        """
        try:
            headers = {}
            if COINGECKO_API_KEY:
                headers['x-cg-demo-api-key'] = COINGECKO_API_KEY

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    'https://api.coingecko.com/api/v3/search',
                    params={'query': query},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            # Extract coins from response
            coins = data.get('coins', [])[:limit]

            # Format results to match Alpaca structure
            results = []
            for coin in coins:
                # CoinGecko uses IDs (bitcoin, ethereum), we need to format for Yahoo Finance
                symbol = coin.get('symbol', '').upper()
                results.append({
                    "symbol": f"{symbol}-USD",  # Format for Yahoo Finance compatibility
                    "name": coin.get('name', symbol),
                    "exchange": "CoinGecko",
                    "asset_class": "crypto",
                    "tradable": False,  # CoinGecko is data-only, not tradable via our system
                    "status": "active",
                    "source": "coingecko",
                    "coingecko_id": coin.get('id'),  # Store ID for future lookups
                    "market_cap_rank": coin.get('market_cap_rank')
                })

            return results

        except Exception as e:
            logger.error(f"CoinGecko search error: {e}")
            return []

    def _merge_crypto_results(
        self,
        alpaca: List[Dict[str, Any]],
        coingecko: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Merge and deduplicate crypto results.

        Args:
            alpaca: Results from Alpaca
            coingecko: Results from CoinGecko
            limit: Max total results

        Returns:
            Merged and deduplicated list (prefers Alpaca)
        """
        seen_symbols = set()
        merged = []

        # Add Alpaca results first (higher quality, tradable)
        for result in alpaca:
            # Extract base currency: "BTC/USD" -> "BTC", "BTC-USD" -> "BTC"
            symbol_base = result["symbol"].split('/')[0].split('-')[0].upper()

            if symbol_base not in seen_symbols:
                seen_symbols.add(symbol_base)
                merged.append(result)

        # Fill with CoinGecko results for missing symbols
        for result in coingecko:
            # Extract base currency from CoinGecko format "BTC-USD" -> "BTC"
            symbol_base = result["symbol"].split('-')[0].upper()

            if symbol_base not in seen_symbols and len(merged) < limit:
                seen_symbols.add(symbol_base)
                merged.append(result)

        return merged[:limit]
