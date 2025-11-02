#!/usr/bin/env python3
"""
Embed Enhanced Pattern Knowledge Base
======================================

Takes the enhanced_pattern_knowledge_base.json (123 patterns)
and generates embeddings for semantic search integration.

Output: enhanced_pattern_knowledge_embedded.json
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from services.knowledge_embedder import KnowledgeEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedPatternEmbedder:
    """
    Embeds the enhanced pattern knowledge base for vector search.
    """
    
    def __init__(self):
        self.embedder = KnowledgeEmbedder()
        self.input_file = Path(__file__).parent / "training/enhanced_pattern_knowledge_base.json"
        self.output_file = Path(__file__).parent / "enhanced_pattern_knowledge_embedded.json"
    
    def _pattern_to_searchable_text(self, pattern_id: str, pattern: Dict[str, Any]) -> str:
        """
        Convert a pattern dict to searchable text for embedding.
        
        Creates a rich text representation including:
        - Pattern name and aliases
        - Category and signal
        - Description and psychology
        - Trading rules and guidance
        - Bulkowski statistics
        """
        parts = []
        
        # Pattern name and aliases
        parts.append(f"Pattern: {pattern.get('name', pattern_id)}")
        aliases = pattern.get('aliases', [])
        if aliases:
            parts.append(f"Also known as: {', '.join(aliases)}")
        
        # Category and signal
        category = pattern.get('category', 'unknown')
        signal = pattern.get('signal', 'neutral')
        parts.append(f"Category: {category}, Signal: {signal}")
        
        # Description
        description = pattern.get('description', '')
        if description:
            parts.append(f"Description: {description}")
        
        # Psychology
        psychology = pattern.get('psychology', '')
        if psychology:
            parts.append(f"Psychology: {psychology}")
        
        # Statistics
        stats = pattern.get('statistics', {})
        if stats:
            bull_rate = stats.get('bull_market_success_rate')
            bear_rate = stats.get('bear_market_success_rate')
            avg_rise = stats.get('average_rise')
            avg_decline = stats.get('average_decline')
            failure_rate = stats.get('failure_rate')
            
            stat_parts = []
            if bull_rate:
                stat_parts.append(f"bull market success rate {bull_rate}%")
            if bear_rate:
                stat_parts.append(f"bear market success rate {bear_rate}%")
            if avg_rise:
                stat_parts.append(f"average rise {avg_rise}%")
            if avg_decline:
                stat_parts.append(f"average decline {avg_decline}%")
            if failure_rate:
                stat_parts.append(f"failure rate {failure_rate}%")
            
            if stat_parts:
                parts.append(f"Statistics: {', '.join(stat_parts)}")
        
        # Trading guidance
        trading = pattern.get('trading', {})
        if trading:
            entry_rules = trading.get('entry_rules', [])
            if entry_rules:
                parts.append(f"Entry rules: {'; '.join(entry_rules)}")
            
            exit_rules = trading.get('exit_rules', [])
            if exit_rules:
                parts.append(f"Exit rules: {'; '.join(exit_rules)}")
            
            stop_loss = trading.get('stop_loss_guidance', '')
            if stop_loss:
                parts.append(f"Stop loss: {stop_loss}")
            
            target = trading.get('target_guidance', '')
            if target:
                parts.append(f"Target: {target}")
            
            rr_ratio = trading.get('risk_reward_ratio')
            if rr_ratio:
                parts.append(f"Risk/reward ratio: {rr_ratio}")
        
        # Bulkowski rank
        rank = pattern.get('bulkowski_rank')
        if rank:
            parts.append(f"Bulkowski rank: {rank}")
        
        # Invalidation
        invalidation = pattern.get('invalidation', {})
        if invalidation:
            conditions = invalidation.get('conditions', [])
            if conditions:
                parts.append(f"Invalidation conditions: {'; '.join(conditions)}")
            
            warnings = invalidation.get('warning_signs', [])
            if warnings:
                parts.append(f"Warning signs: {'; '.join(warnings)}")
        
        return " | ".join(parts)
    
    async def embed_patterns(self):
        """
        Load patterns, convert to chunks, generate embeddings.
        """
        # Load enhanced pattern KB
        logger.info(f"Loading enhanced pattern knowledge base from {self.input_file}")
        
        if not self.input_file.exists():
            logger.error(f"Input file not found: {self.input_file}")
            return
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
        
        patterns = kb_data.get('patterns', {})
        logger.info(f"Found {len(patterns)} patterns to embed")
        
        # Convert patterns to chunks suitable for embedding
        chunks = []
        for pattern_id, pattern in patterns.items():
            # Create searchable text
            searchable_text = self._pattern_to_searchable_text(pattern_id, pattern)
            
            # Create chunk
            chunk = {
                "chunk_id": f"enhanced_pattern_{pattern_id}",
                "doc_id": "enhanced_pattern_knowledge_base",
                "topic": pattern.get('name', pattern_id),
                "pattern_id": pattern_id,
                "category": pattern.get('category', 'unknown'),
                "signal": pattern.get('signal', 'neutral'),
                "source": pattern.get('source', 'Enhanced Pattern KB'),
                "text": searchable_text,
                "metadata": {
                    "pattern_type": pattern_id,
                    "bulkowski_rank": pattern.get('bulkowski_rank'),
                    "success_rate": pattern.get('statistics', {}).get('bull_market_success_rate'),
                }
            }
            
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks for embedding")
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        texts = [chunk['text'] for chunk in chunks]
        
        # Process in batches
        batch_size = 20
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_chunks = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)")
            
            try:
                embeddings = await self.embedder.embed_batch(batch_texts)
                
                # Add embeddings to chunks
                for chunk, embedding in zip(batch_chunks, embeddings):
                    chunk['embedding'] = embedding
                
                logger.info(f"✅ Batch {batch_num}/{total_batches} complete")
                
            except Exception as e:
                logger.error(f"Failed to embed batch {batch_num}: {e}")
                # Add empty embeddings for failed batch
                for chunk in batch_chunks:
                    chunk['embedding'] = []
        
        # Save embedded chunks
        logger.info(f"Saving embedded patterns to {self.output_file}")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2)
        
        # Calculate stats
        embedded_count = sum(1 for c in chunks if c.get('embedding') and len(c['embedding']) > 0)
        file_size_mb = self.output_file.stat().st_size / (1024 * 1024)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ EMBEDDING COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Total patterns: {len(patterns)}")
        logger.info(f"Total chunks: {len(chunks)}")
        logger.info(f"Successfully embedded: {embedded_count}")
        logger.info(f"Output file: {self.output_file}")
        logger.info(f"File size: {file_size_mb:.2f} MB")
        logger.info(f"{'='*70}\n")
        
        return chunks


async def main():
    """Main function to run pattern embedding."""
    embedder = EnhancedPatternEmbedder()
    await embedder.embed_patterns()
    
    print("\n🎉 Enhanced pattern knowledge base has been embedded!")
    print("📁 Output: enhanced_pattern_knowledge_embedded.json")
    print("\n💡 Next steps:")
    print("1. Merge with main knowledge_base_embedded.json, OR")
    print("2. Update VectorRetriever to load both files")


if __name__ == "__main__":
    asyncio.run(main())

