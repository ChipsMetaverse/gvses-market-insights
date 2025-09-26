#!/usr/bin/env python3
"""
Embed Enhanced Knowledge Base
==============================
Generates embeddings for the enhanced knowledge base (1,611 chunks)
extracted from PDFs with 100% coverage.

Run: python3 embed_enhanced_knowledge.py
"""

import asyncio
import json
import logging
import os
from pathlib import Path
import time
from typing import Dict, List
import sys

# Add parent directory to path to import services
sys.path.append(str(Path(__file__).parent))

from services.knowledge_embedder import KnowledgeEmbedder
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedKnowledgeEmbedder:
    """Embedder with progress tracking and validation."""
    
    def __init__(self):
        self.embedder = KnowledgeEmbedder()
        self.stats = {
            'total_chunks': 0,
            'embedded_chunks': 0,
            'failed_chunks': 0,
            'start_time': None,
            'end_time': None,
            'embedding_dimensions': 0,
            'model_used': '',
            'total_tokens': 0
        }
        
    def estimate_tokens(self, text: str) -> int:
        """Rough estimate of tokens (1 token ≈ 4 characters)."""
        return len(text) // 4
        
    async def validate_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Validate chunks before embedding."""
        valid_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Check required fields
            if not chunk.get('text'):
                logger.warning(f"Chunk {i} missing text field, skipping")
                continue
                
            # Estimate tokens
            tokens = self.estimate_tokens(chunk['text'])
            if tokens > 8000:
                logger.warning(f"Chunk {i} exceeds token limit ({tokens} tokens), will be truncated")
                
            valid_chunks.append(chunk)
            
        logger.info(f"Validated {len(valid_chunks)}/{len(chunks)} chunks")
        return valid_chunks
        
    async def embed_with_progress(self, input_file: Path, output_file: Path):
        """Generate embeddings with detailed progress tracking."""
        
        # Load enhanced chunks
        logger.info(f"Loading enhanced chunks from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
            
        self.stats['total_chunks'] = len(chunks)
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"📚 Loaded {len(chunks)} chunks from enhanced extraction")
        
        # Validate chunks
        chunks = await self.validate_chunks(chunks)
        
        # Estimate cost (ada-002: $0.0001 per 1K tokens)
        total_tokens = sum(self.estimate_tokens(c['text']) for c in chunks)
        self.stats['total_tokens'] = total_tokens
        estimated_cost = (total_tokens / 1000) * 0.0001
        logger.info(f"💰 Estimated cost: ${estimated_cost:.2f} for ~{total_tokens:,} tokens")
        
        # Generate embeddings
        logger.info(f"🚀 Starting embedding generation...")
        embedded_chunks = await self.embedder.embed_knowledge_base(
            input_file=str(input_file),
            output_file=str(output_file)
        )
        
        self.stats['embedded_chunks'] = len(embedded_chunks)
        self.stats['failed_chunks'] = len(chunks) - len(embedded_chunks)
        self.stats['end_time'] = datetime.now()
        
        if embedded_chunks:
            self.stats['embedding_dimensions'] = len(embedded_chunks[0]['embedding'])
            self.stats['model_used'] = self.embedder.embedding_model
            
        return embedded_chunks
        
    def print_summary(self):
        """Print embedding generation summary."""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print("\n" + "=" * 80)
        print("EMBEDDING GENERATION SUMMARY")
        print("=" * 80)
        print(f"📊 Total chunks processed: {self.stats['total_chunks']}")
        print(f"✅ Successfully embedded: {self.stats['embedded_chunks']}")
        print(f"❌ Failed embeddings: {self.stats['failed_chunks']}")
        print(f"📏 Embedding dimensions: {self.stats['embedding_dimensions']}")
        print(f"🤖 Model used: {self.stats['model_used']}")
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print(f"💾 Tokens processed: ~{self.stats['total_tokens']:,}")
        print(f"🎯 Success rate: {self.stats['embedded_chunks']/self.stats['total_chunks']*100:.1f}%")
        print("=" * 80)


async def verify_embeddings(output_file: Path):
    """Verify the generated embeddings."""
    logger.info("\n🔍 Verifying embeddings...")
    
    with open(output_file, 'r', encoding='utf-8') as f:
        embedded_chunks = json.load(f)
        
    # Check all chunks have embeddings
    chunks_with_embeddings = sum(1 for c in embedded_chunks if c.get('embedding'))
    
    # Sample embedding check
    if embedded_chunks:
        sample = embedded_chunks[0]
        dim = len(sample['embedding']) if sample.get('embedding') else 0
        
        logger.info(f"✓ Total chunks: {len(embedded_chunks)}")
        logger.info(f"✓ Chunks with embeddings: {chunks_with_embeddings}")
        logger.info(f"✓ Embedding dimensions: {dim}")
        logger.info(f"✓ Sample text preview: {sample['text'][:100]}...")
        
        # Check for variety in sources
        sources = set(c.get('source', 'unknown') for c in embedded_chunks[:100])
        logger.info(f"✓ Source diversity (first 100): {len(sources)} unique sources")
        
    return chunks_with_embeddings == len(embedded_chunks)


async def main():
    """Main embedding generation process."""
    
    # File paths
    base_dir = Path(__file__).parent
    input_file = base_dir / "knowledge_base_enhanced.json"
    output_file = base_dir / "knowledge_base_enhanced_embedded.json"
    
    # Check input exists
    if not input_file.exists():
        logger.error(f"❌ Input file not found: {input_file}")
        logger.error("Run enhanced_extract_knowledge.py first!")
        return
        
    # Check if output already exists
    if output_file.exists():
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        logger.warning(f"⚠️ Output file already exists ({file_size:.1f} MB)")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            logger.info("Aborted.")
            return
            
    # Create embedder
    embedder = EnhancedKnowledgeEmbedder()
    
    try:
        # Generate embeddings
        embedded_chunks = await embedder.embed_with_progress(input_file, output_file)
        
        # Print summary
        embedder.print_summary()
        
        # Verify results
        if await verify_embeddings(output_file):
            logger.info("\n✅ Embedding generation complete and verified!")
            logger.info(f"📦 Output saved to: {output_file}")
            
            # Calculate file size
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"📏 File size: {file_size:.1f} MB")
            
            # Next steps
            print("\n📋 Next Steps:")
            print("1. Archive old embeddings: mv knowledge_base_embedded.json knowledge_base_embedded.json.backup")
            print("2. Deploy new embeddings: mv knowledge_base_enhanced_embedded.json knowledge_base_embedded.json")
            print("3. Update knowledge base: mv knowledge_base_enhanced.json knowledge_base.json")
            print("4. Restart backend: uvicorn mcp_server:app --reload")
            print("5. Run tests: python3 test_backward_compatibility.py")
            
        else:
            logger.error("❌ Embedding verification failed!")
            
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        exit(1)
        
    asyncio.run(main())