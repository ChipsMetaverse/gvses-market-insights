"""
Knowledge Embedder Service
==========================
Generates embeddings for knowledge base chunks using OpenAI's embedding API.
"""

import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
import time

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeEmbedder:
    """
    Service to generate embeddings for knowledge base chunks.
    Uses OpenAI's text-embedding-ada-002 model which is widely available.
    Falls back to text-embedding-3-large if ada-002 fails.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Primary model - ada-002 is cheaper and widely available (1536 dimensions)
        self.primary_model = "text-embedding-ada-002"
        # Fallback model - 3-large is more powerful (3072 dimensions)
        self.fallback_model = "text-embedding-3-large"
        self.embedding_model = self.primary_model  # Start with primary
        self.batch_size = 20  # Smaller batches to avoid rate limits
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text with fallback."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Truncate to model's context limit
            )
            return response.data[0].embedding
        except Exception as e:
            # If primary model fails and we haven't tried fallback yet
            if self.embedding_model == self.primary_model:
                logger.warning(f"Primary model {self.primary_model} failed: {e}")
                logger.info(f"Trying fallback model {self.fallback_model}...")
                self.embedding_model = self.fallback_model
                try:
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=text[:8000]
                    )
                    logger.info(f"Fallback model {self.fallback_model} succeeded")
                    return response.data[0].embedding
                except Exception as fallback_error:
                    logger.error(f"Both models failed: {fallback_error}")
                    return []
            else:
                logger.error(f"Failed to generate embedding: {e}")
                return []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts with fallback."""
        try:
            # Truncate texts to model limit
            truncated_texts = [text[:8000] for text in texts]
            
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=truncated_texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            # If primary model fails and we haven't tried fallback yet
            if self.embedding_model == self.primary_model:
                logger.warning(f"Primary model {self.primary_model} failed for batch: {e}")
                logger.info(f"Trying fallback model {self.fallback_model} for batch...")
                self.embedding_model = self.fallback_model
                try:
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=truncated_texts
                    )
                    logger.info(f"Fallback model {self.fallback_model} succeeded for batch")
                    return [data.embedding for data in response.data]
                except Exception as fallback_error:
                    logger.error(f"Both models failed for batch: {fallback_error}")
                    return [[] for _ in texts]
            else:
                logger.error(f"Failed to generate batch embeddings: {e}")
                return [[] for _ in texts]
    
    async def embed_knowledge_base(self, input_file: str = None, output_file: str = None):
        """
        Generate embeddings for all chunks in the knowledge base.
        
        Args:
            input_file: Path to input JSON file with chunks
            output_file: Path to output JSON file with embeddings
        """
        # Default paths
        if input_file is None:
            input_file = Path(__file__).parent.parent / "knowledge_base.json"
        if output_file is None:
            output_file = Path(__file__).parent.parent / "knowledge_base_embedded.json"
        
        # Load chunks
        logger.info(f"Loading chunks from {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Process in batches
        embedded_chunks = []
        total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_texts = [chunk["text"] for chunk in batch]
            batch_num = i // self.batch_size + 1
            
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
            
            # Generate embeddings for batch
            embeddings = await self.embed_batch(batch_texts)
            
            # Add embeddings to chunks
            for chunk, embedding in zip(batch, embeddings):
                if embedding:  # Only add if embedding was successful
                    chunk["embedding"] = embedding
                    embedded_chunks.append(chunk)
                else:
                    logger.warning(f"Skipping chunk without embedding: {chunk.get('source', 'unknown')}")
            
            # Rate limit protection
            if batch_num < total_batches:
                await asyncio.sleep(0.5)  # Small delay between batches
        
        # Save embedded chunks
        logger.info(f"Saving {len(embedded_chunks)} embedded chunks to {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(embedded_chunks, f, indent=2, ensure_ascii=False)
        
        # Print statistics
        logger.info(f"\n✅ Successfully embedded {len(embedded_chunks)}/{len(chunks)} chunks")
        if embedded_chunks:
            logger.info(f"   Embedding model used: {self.embedding_model}")
            logger.info(f"   Embedding dimensions: {len(embedded_chunks[0]['embedding'])}")
        logger.info(f"   Output saved to: {output_file}")
        
        return embedded_chunks
    
    async def update_embeddings(self, chunks_to_update: List[Dict[str, Any]]):
        """
        Update embeddings for specific chunks (e.g., after adding new documents).
        
        Args:
            chunks_to_update: List of chunks that need embedding updates
        """
        logger.info(f"Updating embeddings for {len(chunks_to_update)} chunks")
        
        for chunk in chunks_to_update:
            if "text" in chunk:
                embedding = await self.embed_text(chunk["text"])
                if embedding:
                    chunk["embedding"] = embedding
                    
        return chunks_to_update


async def main():
    """Main function to run embedding generation."""
    embedder = KnowledgeEmbedder()
    await embedder.embed_knowledge_base()


if __name__ == "__main__":
    # Run the embedding process
    asyncio.run(main())