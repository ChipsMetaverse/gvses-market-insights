"""
Vector Retriever Service
========================
Retrieves relevant knowledge from the embedded knowledge base using
cosine similarity for semantic search.
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from openai import AsyncOpenAI
import asyncio
import os
from dotenv import load_dotenv
import hashlib
import re
import sys
from pathlib import Path

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    Retrieves relevant knowledge chunks using vector similarity search.
    Uses cosine similarity to find semantically similar content.
    """
    
    def __init__(self, embedded_file: str = None, include_enhanced_patterns: bool = True):
        """
        Initialize the vector retriever.
        
        Args:
            embedded_file: Path to the embedded knowledge base JSON file
            include_enhanced_patterns: Whether to load enhanced pattern knowledge (default: True)
        """
        if embedded_file is None:
            embedded_file = Path(__file__).parent.parent / "knowledge_base_embedded.json"
        
        # Load main knowledge base
        self.knowledge_base = self._load_embedded_knowledge(embedded_file)
        
        # Load enhanced pattern knowledge base and merge
        if include_enhanced_patterns:
            enhanced_patterns_file = Path(__file__).parent.parent / "enhanced_pattern_knowledge_embedded.json"
            enhanced_patterns = self._load_embedded_knowledge(enhanced_patterns_file)
            if enhanced_patterns:
                logger.info(f"✅ Loaded {len(enhanced_patterns)} enhanced pattern chunks")
                self.knowledge_base.extend(enhanced_patterns)
                logger.info(f"📊 Total knowledge base: {len(self.knowledge_base)} chunks")
        
        self.embeddings_matrix = None
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Auto-detect embedding model based on dimension
        if self.knowledge_base and self.knowledge_base[0].get("embedding"):
            embedding_dim = len(self.knowledge_base[0]["embedding"])
            if embedding_dim == 1536:
                self.embedding_model = "text-embedding-3-small"  # 1536 dimensions
            elif embedding_dim == 3072:
                self.embedding_model = "text-embedding-3-large"  # 3072 dimensions
            else:
                self.embedding_model = "text-embedding-ada-002"  # Default fallback
            logger.info(f"Detected embedding dimension: {embedding_dim}, using model: {self.embedding_model}")
        else:
            self.embedding_model = "text-embedding-3-small"  # Safe default
        
        # Initialize embedding cache
        self.embedding_cache = {}  # Maps query text to embedding
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Fallback training docs cache (raw chunks)
        self._training_docs_cache: Dict[str, List[Dict[str, Any]]] = {}
        
        # Build embeddings matrix for efficient search
        if self.knowledge_base:
            self._build_embeddings_matrix()
            logger.info(f"Loaded {len(self.knowledge_base)} total embedded chunks")
            logger.info(f"Embeddings matrix shape: {self.embeddings_matrix.shape}")
        
    def _load_embedded_knowledge(self, embedded_file: Path) -> List[Dict[str, Any]]:
        """Load the embedded knowledge base from JSON file."""
        try:
            with open(embedded_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
                # Filter out chunks without embeddings
                embedded_chunks = [c for c in chunks if 'embedding' in c and c['embedding']]
                logger.info(f"Loaded {len(embedded_chunks)} chunks with embeddings")
                return embedded_chunks
        except FileNotFoundError:
            logger.warning(f"Embedded knowledge base not found at {embedded_file}")
            return []
        except Exception as e:
            logger.error(f"Failed to load embedded knowledge base: {e}")
            return []
    
    def _build_embeddings_matrix(self):
        """Build a numpy matrix of all embeddings for efficient computation."""
        if not self.knowledge_base:
            return
        
        embeddings_list = [chunk['embedding'] for chunk in self.knowledge_base]
        self.embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
        
        # Normalize embeddings for cosine similarity (dot product of normalized vectors)
        norms = np.linalg.norm(self.embeddings_matrix, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        self.embeddings_matrix = self.embeddings_matrix / norms
    
    def _cosine_similarity(self, query_embedding: np.ndarray, 
                          chunk_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and chunk embeddings.
        
        Args:
            query_embedding: Query embedding vector (normalized)
            chunk_embeddings: Matrix of chunk embeddings (normalized)
            
        Returns:
            Array of similarity scores
        """
        # Since vectors are normalized, cosine similarity is just dot product
        return np.dot(chunk_embeddings, query_embedding)
    
    async def embed_query(self, query: str) -> Optional[List[float]]:
        """Generate embedding for a query text with caching."""
        # Check cache first
        cache_key = query[:8000]  # Use truncated query as cache key
        if cache_key in self.embedding_cache:
            self.cache_hits += 1
            logger.debug(f"Embedding cache hit (total hits: {self.cache_hits})")
            return self.embedding_cache[cache_key]
        
        # Cache miss - generate embedding
        self.cache_misses += 1
        logger.debug(f"Embedding cache miss (total misses: {self.cache_misses})")
        
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=query[:8000]  # Truncate if necessary
            )
            embedding = response.data[0].embedding
            
            # Store in cache (limit cache size to prevent memory issues)
            if len(self.embedding_cache) < 1000:  # Max 1000 cached embeddings
                self.embedding_cache[cache_key] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Embedding failed: {type(e).__name__}: {e}", exc_info=True)
            raise
    
    async def search_knowledge(self, query: str, top_k: int = 3, 
                              min_score: float = 0.65) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge chunks using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            min_score: Minimum similarity score threshold (0-1)
            
        Returns:
            List of relevant knowledge chunks with similarity scores
        """
        if not self.knowledge_base or self.embeddings_matrix is None:
            logger.warning("No embedded knowledge available – using raw-docs fallback if present")
            return self._fallback_search_training_docs(query, top_k=top_k)
        
        # Generate embedding for query
        query_embedding = await self.embed_query(query)
        if query_embedding is None:
            logger.warning("Failed to embed query, falling back to empty results")
            return []
        
        # Normalize query embedding
        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm
        
        # Calculate similarities
        similarities = self._cosine_similarity(query_vec, self.embeddings_matrix)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                chunk = self.knowledge_base[idx].copy()
                # Remove embedding from result to reduce size
                chunk.pop('embedding', None)
                chunk['similarity_score'] = score
                results.append(chunk)
        
        if results:
            logger.info(f"Found {len(results)} relevant chunks for query: '{query[:50]}...'")
            logger.info(f"Top similarity score: {results[0]['similarity_score']:.3f}")
        else:
            logger.info(f"No chunks found above threshold {min_score} for query: '{query[:50]}...' – trying raw-docs fallback")
            results = self._fallback_search_training_docs(query, top_k=top_k)
        
        return results

    # ------------------------------------------------------------------
    # Raw-docs fallback: loads training json_docs and does keyword scoring
    # ------------------------------------------------------------------
    def _load_training_doc(self, name: str) -> List[Dict[str, Any]]:
        if name in self._training_docs_cache:
            return self._training_docs_cache[name]
        try:
            base = Path(__file__).resolve().parents[1] / 'training' / 'json_docs'
            path = base / name
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chunks = data.get('chunks', [])
            # Normalize to common format
            norm = []
            for ch in chunks:
                norm.append({
                    'id': ch.get('chunk_id', ''),
                    'text': ch.get('text', ''),
                    'source': 'Encyclopedia of Chart Patterns' if 'encyclopedia' in name else name,
                    'source_file': name,
                })
            self._training_docs_cache[name] = norm
            logger.info(f"Loaded {len(norm)} raw chunks from {name}")
            return norm
        except Exception as e:
            logger.warning(f"Failed to load training doc {name}: {e}")
            self._training_docs_cache[name] = []
            return []

    def _fallback_search_training_docs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        docs = []
        # Focus on encyclopedia_of_chart_patterns per request
        docs.extend(self._load_training_doc('encyclopedia_of_chart_patterns.json'))
        docs.extend(self._load_training_doc('price-action-patterns.json'))
        docs.extend(self._load_training_doc('the_candlestick_trading_bible.json'))
        docs.extend(self._load_training_doc('the-candlestick-trading-bible.json'))
        docs.extend(self._load_training_doc('technical_analysis_for_dummies_2nd_edition.json'))
        if not docs:
            return []
        # Simple keyword scoring
        q = query.lower()
        tokens = [t for t in re.split(r"[^a-z0-9]+", q) if len(t) > 2]
        if not tokens:
            tokens = q.split()
        scored = []
        for ch in docs:
            text_l = ch.get('text', '').lower()
            if not text_l:
                continue
            score = 0
            for t in tokens:
                # weight frequent TA terms slightly more
                w = 2 if t in {'pattern','triangle','flag','wedge','head','shoulders','double','triple','breakout','pennant','rectangle','gap','doji','hammer','harami','engulfing'} else 1
                if t in text_l:
                    score += w
            if score > 0:
                item = ch.copy()
                item['similarity_score'] = min(0.99, 0.5 + 0.01 * score)
                # naive topic extraction: first TA keyword hit
                topic = None
                for key in ['head and shoulders','double top','double bottom','triple top','triple bottom','ascending triangle','descending triangle','symmetrical triangle','flag','pennant','wedge','rectangle','broadening','diamond','rounding bottom','doji','hammer','harami','engulfing','marubozu']:
                    if key in text_l:
                        topic = key
                        break
                if topic:
                    item['topic'] = topic
                docs_path = ch.get('source_file', 'encyclopedia_of_chart_patterns.json')
                item['source'] = 'Encyclopedia of Chart Patterns'
                scored.append(item)
        scored.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored[:top_k]
    
    async def prewarm_embeddings(self, queries: List[str]) -> int:
        """
        Pre-warm the embedding cache with common queries.
        
        Args:
            queries: List of common queries to pre-compute embeddings for
            
        Returns:
            Number of embeddings successfully cached
        """
        cached_count = 0
        for query in queries:
            try:
                # This will cache the embedding if not already cached
                await self.embed_query(query)
                cached_count += 1
            except Exception as e:
                logger.warning(f"Failed to pre-warm embedding for '{query[:50]}...': {e}")
        
        logger.info(f"Pre-warmed {cached_count} embeddings. Cache size: {len(self.embedding_cache)}")
        return cached_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "cache_size": len(self.embedding_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate
        }
    
    async def get_pattern_knowledge(self, pattern_type: str) -> List[Dict[str, Any]]:
        """
        Get specific knowledge about a pattern type using semantic search.
        
        Args:
            pattern_type: Type of pattern (e.g., "bullish_engulfing", "double_bottom")
            
        Returns:
            List of relevant chunks about the pattern
        """
        # Convert pattern type to natural language query
        pattern_query = f"explain {pattern_type.replace('_', ' ')} pattern formation recognition trading"
        
        # Search with higher threshold for pattern-specific content
        results = await self.search_knowledge(pattern_query, top_k=3, min_score=0.75)
        
        # Additional filtering for high relevance
        pattern_results = []
        for result in results:
            # Check if pattern is mentioned in topic or text
            if (pattern_type.lower() in result.get('topic', '').lower() or 
                pattern_type.replace('_', ' ').lower() in result.get('text', '').lower()[:500]):
                pattern_results.append(result)
        
        return pattern_results if pattern_results else results[:2]
    
    async def get_indicator_knowledge(self, indicator: str, 
                                     value: float = None) -> List[Dict[str, Any]]:
        """
        Get knowledge about a specific indicator using semantic search.
        
        Args:
            indicator: Indicator name (e.g., "RSI", "MACD")
            value: Optional indicator value for context-specific search
            
        Returns:
            List of relevant chunks about the indicator
        """
        # Build contextual query based on indicator and value
        query_parts = [indicator]
        
        if value is not None:
            if indicator.upper() == "RSI":
                if value > 70:
                    query_parts.extend(["overbought", "sell signal", "reversal"])
                elif value < 30:
                    query_parts.extend(["oversold", "buy signal", "bounce"])
                else:
                    query_parts.extend(["neutral", "consolidation"])
            elif indicator.upper() == "MACD":
                query_parts.extend(["signal line", "crossover", "divergence"])
                if value > 0:
                    query_parts.append("bullish")
                else:
                    query_parts.append("bearish")
        
        query = " ".join(query_parts) + " technical indicator trading strategy"
        
        return await self.search_knowledge(query, top_k=3, min_score=0.7)
    
    async def get_strategy_knowledge(self, market_condition: str) -> List[Dict[str, Any]]:
        """
        Get trading strategy knowledge for specific market conditions.
        
        Args:
            market_condition: Market condition (e.g., "trending", "ranging", "volatile")
            
        Returns:
            List of relevant strategy chunks
        """
        # Build comprehensive strategy query
        query = f"{market_condition} market trading strategy risk management position sizing entry exit"
        
        results = await self.search_knowledge(query, top_k=4, min_score=0.68)
        
        # Prioritize strategy-specific content
        strategy_results = []
        other_results = []
        
        for result in results:
            topic = result.get('topic', '').lower()
            if 'strategy' in topic or 'risk' in topic or 'management' in topic:
                strategy_results.append(result)
            else:
                other_results.append(result)
        
        # Return strategy results first, then others
        return strategy_results + other_results
    
    def format_knowledge_for_agent(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format knowledge chunks into a string for agent consumption.
        
        Args:
            chunks: List of knowledge chunks with similarity scores
            
        Returns:
            Formatted string with citations and relevance scores
        """
        if not chunks:
            return ""
        
        formatted_parts = []
        for i, chunk in enumerate(chunks[:3], 1):  # Limit to top 3 chunks
            source = chunk.get('source', 'Unknown')
            page = chunk.get('page', '')
            text = chunk.get('text', '')[:500]  # Truncate long texts
            score = chunk.get('similarity_score', 0)
            
            # Clean up text
            import re
            text = re.sub(r'\s+', ' ', text).strip()
            
            citation = f"[{i}. {source}"
            if page:
                citation += f", p.{page}"
            citation += f" | Relevance: {score:.1%}]"
            
            formatted_parts.append(f"{citation}\n{text}")
        
        return "\n\n".join(formatted_parts)


# Example usage
async def main():
    retriever = VectorRetriever()
    
    # Test pattern search
    print("\n=== Testing Pattern Search (Vector) ===")
    results = await retriever.get_pattern_knowledge("bullish_engulfing")
    for r in results:
        print(f"Score: {r.get('similarity_score', 0):.3f} - Topic: {r['topic']} - Source: {r['source']}")
    
    # Test indicator search
    print("\n=== Testing Indicator Search (Vector) ===")
    results = await retriever.get_indicator_knowledge("RSI", 75)
    for r in results:
        print(f"Score: {r.get('similarity_score', 0):.3f} - Topic: {r['topic']} - Source: {r['source']}")
    
    # Test general search
    print("\n=== Testing General Search (Vector) ===")
    results = await retriever.search_knowledge("how to identify support and resistance levels in trading")
    for r in results:
        print(f"Score: {r.get('similarity_score', 0):.3f} - Topic: {r['topic']} - Source: {r['source']}")
    
    # Compare with complex query
    print("\n=== Testing Complex Query (Vector) ===")
    results = await retriever.search_knowledge("what are the best momentum indicators for day trading volatile stocks")
    formatted = retriever.format_knowledge_for_agent(results)
    print(formatted[:500] + "..." if len(formatted) > 500 else formatted)


if __name__ == "__main__":
    asyncio.run(main())
