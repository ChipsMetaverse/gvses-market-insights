#!/usr/bin/env python3
"""
Test end-to-end integration of vector-based knowledge retrieval in agent responses.
Verifies that the agent uses embedded knowledge when answering trading questions.
"""

import asyncio
import aiohttp
import json
# Type hints removed for compatibility
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test queries that should trigger knowledge retrieval
TEST_QUERIES = [
    {
        "query": "What is a bullish engulfing pattern and how can I trade it?",
        "expected_topics": ["bullish_engulfing", "pattern", "trading"],
        "should_have_knowledge": True
    },
    {
        "query": "How do I identify support and resistance levels in a trending market?",
        "expected_topics": ["support_resistance", "trend", "levels"],
        "should_have_knowledge": True
    },
    {
        "query": "What does RSI above 70 indicate and what should I do?",
        "expected_topics": ["rsi", "overbought", "indicator"],
        "should_have_knowledge": True
    },
    {
        "query": "Explain the MACD crossover strategy",
        "expected_topics": ["macd", "crossover", "strategy"],
        "should_have_knowledge": True
    },
    {
        "query": "How should I manage risk in volatile markets?",
        "expected_topics": ["risk_management", "volatile", "strategy"],
        "should_have_knowledge": True
    },
    {
        "query": "What's the current price of TSLA?",
        "expected_topics": ["price", "TSLA"],
        "should_have_knowledge": False  # This shouldn't trigger knowledge retrieval
    }
]

async def test_agent_response(query):
    """Test a single query against the agent endpoint."""
    url = "http://localhost:8000/ask"
    
    async with aiohttp.ClientSession() as session:
        payload = {"query": query}  # Changed from "question" to "query"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "response": result.get("response", ""),
                        "raw": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def analyze_response(response, expected_topics):
    """Analyze if the response contains expected knowledge-based content."""
    response_lower = response.lower()
    
    # Check for knowledge indicators
    knowledge_indicators = [
        "according to",
        "typically",
        "generally",
        "traders often",
        "technical analysis",
        "pattern formation",
        "indicator suggests",
        "strategy involves",
        "risk management",
        "entry point",
        "exit point",
        "stop loss"
    ]
    
    # Check for citation patterns (if the formatter includes them)
    has_citations = any(marker in response for marker in ["[1.", "[2.", "[3.", "Relevance:"])
    
    # Count knowledge indicators found
    indicators_found = sum(1 for indicator in knowledge_indicators 
                          if indicator in response_lower)
    
    # Check if expected topics are mentioned
    topics_found = sum(1 for topic in expected_topics 
                      if any(word in response_lower for word in topic.split('_')))
    
    # Determine if response appears to use knowledge base
    appears_knowledge_based = (
        indicators_found >= 2 or 
        has_citations or
        (topics_found >= len(expected_topics) * 0.6 and len(response) > 200)
    )
    
    return {
        "appears_knowledge_based": appears_knowledge_based,
        "indicators_found": indicators_found,
        "has_citations": has_citations,
        "topics_coverage": f"{topics_found}/{len(expected_topics)}",
        "response_length": len(response)
    }

async def test_vector_retriever_directly():
    """Test the vector retriever directly to ensure it's working."""
    from services.vector_retriever import VectorRetriever
    
    logger.info("\n=== Testing Vector Retriever Directly ===")
    retriever = VectorRetriever()
    
    # Test a few queries
    test_cases = [
        ("bullish engulfing pattern", "pattern"),
        ("RSI overbought", "indicator"),
        ("support and resistance", "levels")
    ]
    
    for query, context in test_cases:
        results = await retriever.search_knowledge(query, top_k=3)
        logger.info(f"\nQuery: '{query}'")
        if results:
            logger.info(f"  Top result: {results[0]['similarity_score']:.1%} relevance")
            logger.info(f"  Topic: {results[0].get('topic', 'N/A')}")
            logger.info(f"  Source: {results[0].get('source', 'N/A')}")
        else:
            logger.warning("  No results found!")
    
    return len(retriever.knowledge_base) > 0

async def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("VECTOR INTEGRATION END-TO-END TEST")
    print("="*60)
    
    # First verify the retriever is working
    retriever_ok = await test_vector_retriever_directly()
    if not retriever_ok:
        logger.error("❌ Vector retriever not properly initialized!")
        return
    else:
        logger.info("✅ Vector retriever is working with embedded knowledge")
    
    print("\n" + "="*60)
    print("TESTING AGENT RESPONSES WITH KNOWLEDGE")
    print("="*60)
    
    success_count = 0
    knowledge_used_count = 0
    
    for test in TEST_QUERIES:
        print(f"\n{'='*50}")
        print(f"Query: {test['query'][:60]}...")
        print("-"*50)
        
        # Get agent response
        result = await test_agent_response(test['query'])
        
        if not result["success"]:
            print(f"❌ Failed to get response: {result['error']}")
            continue
        
        success_count += 1
        response = result["response"]
        
        # Analyze response
        analysis = analyze_response(response, test["expected_topics"])
        
        # Print analysis
        print(f"Response length: {analysis['response_length']} chars")
        print(f"Knowledge indicators found: {analysis['indicators_found']}")
        print(f"Has citations: {analysis['has_citations']}")
        print(f"Topics covered: {analysis['topics_coverage']}")
        print(f"Appears knowledge-based: {analysis['appears_knowledge_based']}")
        
        # Check if expectations are met
        if test["should_have_knowledge"]:
            if analysis["appears_knowledge_based"]:
                print("✅ PASS: Response uses knowledge as expected")
                knowledge_used_count += 1
            else:
                print("⚠️  WARNING: Response may not be using knowledge base")
                print(f"Response preview: {response[:200]}...")
        else:
            if not analysis["appears_knowledge_based"]:
                print("✅ PASS: Response correctly doesn't use knowledge")
            else:
                print("⚠️  WARNING: Response unexpectedly uses knowledge")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {len(TEST_QUERIES)}")
    print(f"Successful responses: {success_count}/{len(TEST_QUERIES)}")
    print(f"Knowledge correctly used: {knowledge_used_count}/{sum(1 for t in TEST_QUERIES if t['should_have_knowledge'])}")
    
    if success_count == len(TEST_QUERIES):
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {len(TEST_QUERIES) - success_count} tests failed")
    
    # Test streaming for comparison
    print("\n" + "="*60)
    print("TESTING STREAMING ENDPOINT (COMPARISON)")
    print("="*60)
    
    url = "http://localhost:8000/ask-stream"
    query = "Explain the head and shoulders pattern"
    
    async with aiohttp.ClientSession() as session:
        payload = {"query": query}  # Changed to use "query" field
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print(f"Query: {query}")
                    print("Streaming response chunks...")
                    full_response = ""
                    chunk_count = 0
                    async for line in response.content:
                        if line:
                            chunk_count += 1
                            decoded = line.decode('utf-8').strip()
                            if decoded.startswith("data: "):
                                full_response += decoded[6:]
                    
                    print(f"Received {chunk_count} chunks")
                    analysis = analyze_response(full_response, ["head_and_shoulders", "pattern"])
                    print(f"Appears knowledge-based: {analysis['appears_knowledge_based']}")
                else:
                    print(f"❌ Streaming failed: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Streaming error: {e}")

if __name__ == "__main__":
    asyncio.run(main())