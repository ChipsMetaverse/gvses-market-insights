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

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    Retrieves relevant knowledge chunks using vector similarity search.
    Uses cosine similarity to find semantically similar content.
    """
    
    def __init__(self, embedded_file: str = None):
        """
        Initialize the vector retriever.
        
        Args:
            embedded_file: Path to the embedded knowledge base JSON file
        """
        if embedded_file is None:
            embedded_file = Path(__file__).parent.parent / "knowledge_base_embedded.json"
        
        self.knowledge_base = self._load_embedded_knowledge(embedded_file)
        self.embeddings_matrix = None
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"  # Match what we used for generation
        
        # Build embeddings matrix for efficient search
        if self.knowledge_base:
            self._build_embeddings_matrix()
            logger.info(f"Loaded {len(self.knowledge_base)} embedded chunks")
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
        """Generate embedding for a query text."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=query[:8000]  # Truncate if necessary
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            return None
    
    async def search_knowledge(self, query: str, top_k: int = 5, 
                              min_score: float = 0.7) -> List[Dict[str, Any]]:
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
            logger.warning("No embedded knowledge available")
            return []
        
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
            logger.info(f"No chunks found above threshold {min_score} for query: '{query[:50]}...'")
        
        return results
    
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