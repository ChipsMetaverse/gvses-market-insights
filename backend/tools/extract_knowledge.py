#!/usr/bin/env python3
"""
Extract and process knowledge from PDF files in the training/knowledge directory.
Creates structured JSON chunks for embedding and retrieval.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
import pypdf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker for reference
                        text_content.append(f"\n[Page {page_num + 1}]\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num + 1} from {pdf_path.name}: {e}")
            
            return "\n".join(text_content)
    except Exception as e:
        logger.error(f"Failed to read PDF {pdf_path}: {e}")
        return ""


def detect_topic(text: str) -> str:
    """Detect the primary topic of a text chunk."""
    text_lower = text.lower()
    
    # Pattern detection
    patterns = {
        "head_and_shoulders": ["head and shoulders", "h&s pattern", "neckline"],
        "double_bottom": ["double bottom", "w pattern", "twin valleys"],
        "double_top": ["double top", "m pattern", "twin peaks"],
        "triangle": ["triangle", "ascending triangle", "descending triangle", "symmetrical"],
        "flag": ["flag pattern", "bull flag", "bear flag", "pennant"],
        "wedge": ["wedge", "rising wedge", "falling wedge"],
        "cup_and_handle": ["cup and handle", "cup with handle", "c&h"],
        "engulfing": ["engulfing", "bullish engulfing", "bearish engulfing"],
        "doji": ["doji", "dragonfly", "gravestone", "long-legged"],
        "hammer": ["hammer", "inverted hammer", "hanging man"],
        "shooting_star": ["shooting star", "evening star", "morning star"],
        "support_resistance": ["support", "resistance", "key level", "price level"],
        "trend": ["trend", "uptrend", "downtrend", "trend line"],
        "volume": ["volume", "volume analysis", "volume spike", "volume pattern"],
        "rsi": ["rsi", "relative strength", "overbought", "oversold"],
        "macd": ["macd", "signal line", "histogram", "convergence divergence"],
        "moving_average": ["moving average", "ma", "sma", "ema", "golden cross", "death cross"],
        "bollinger": ["bollinger", "bands", "squeeze", "expansion"],
        "risk_management": ["risk", "stop loss", "position size", "risk reward"],
        "strategy": ["strategy", "trading plan", "entry", "exit", "setup"]
    }
    
    # Count pattern mentions
    topic_scores = {}
    for topic, keywords in patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            topic_scores[topic] = score
    
    # Return the highest scoring topic, or "general" if none found
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    return "general_ta"


def chunk_text(text: str, max_tokens: int = 400, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Chunk text into smaller segments with metadata.
    Approximates tokens as words * 1.3 (rough estimate).
    """
    # Split by paragraphs first to maintain context
    paragraphs = re.split(r'\n\n+', text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    page_num = 1
    
    for para in paragraphs:
        # Track page numbers
        if "[Page" in para:
            page_match = re.search(r'\[Page (\d+)\]', para)
            if page_match:
                page_num = int(page_match.group(1))
                para = re.sub(r'\[Page \d+\]', '', para).strip()
        
        # Estimate tokens (words * 1.3)
        para_tokens = len(para.split()) * 1.3
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "tokens": int(current_tokens),
                "page": page_num,
                "topic": detect_topic(chunk_text)
            })
            
            # Start new chunk with overlap
            if overlap > 0 and current_chunk:
                # Keep last paragraph for context
                current_chunk = [current_chunk[-1], para]
                current_tokens = len(current_chunk[-1].split()) * 1.3 + para_tokens
            else:
                current_chunk = [para]
                current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "tokens": int(current_tokens),
            "page": page_num,
            "topic": detect_topic(chunk_text)
        })
    
    return chunks


def extract_knowledge_base():
    """Main function to extract and process all PDFs."""
    knowledge_dir = Path(__file__).parent.parent / "training" / "knowledge"
    output_file = Path(__file__).parent.parent / "knowledge_base.json"
    
    if not knowledge_dir.exists():
        logger.error(f"Knowledge directory not found: {knowledge_dir}")
        return
    
    all_chunks = []
    pdf_files = list(knowledge_dir.glob("*.pdf"))
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        logger.info(f"Processing {pdf_file.name}...")
        
        # Extract text
        text = extract_pdf_text(pdf_file)
        if not text:
            logger.warning(f"No text extracted from {pdf_file.name}")
            continue
        
        # Chunk the text
        chunks = chunk_text(text, max_tokens=400)
        
        # Add source metadata to each chunk
        for chunk in chunks:
            chunk["source"] = pdf_file.name
            chunk["source_type"] = "pdf"
            all_chunks.append(chunk)
        
        logger.info(f"  Extracted {len(chunks)} chunks from {pdf_file.name}")
    
    # Save to JSON
    logger.info(f"Saving {len(all_chunks)} total chunks to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    topics = {}
    for chunk in all_chunks:
        topic = chunk.get("topic", "unknown")
        topics[topic] = topics.get(topic, 0) + 1
    
    logger.info("\nChunk Statistics by Topic:")
    for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {topic}: {count} chunks")
    
    logger.info(f"\nTotal chunks: {len(all_chunks)}")
    logger.info(f"Average chunk size: {sum(c['tokens'] for c in all_chunks) / len(all_chunks):.0f} tokens")
    
    return all_chunks


if __name__ == "__main__":
    chunks = extract_knowledge_base()
    if chunks:
        print(f"\n✅ Successfully extracted {len(chunks)} knowledge chunks")
        print(f"   Output saved to: backend/knowledge_base.json")
    else:
        print("\n❌ Failed to extract knowledge")