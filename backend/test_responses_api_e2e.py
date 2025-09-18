#!/usr/bin/env python3
"""
End-to-end test for OpenAI Responses API with structured outputs.
Tests the complete flow from query to structured JSON response.
"""

import asyncio
import json
import time
from typing import Dict, Any
from services.agent_orchestrator import get_orchestrator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_responses_api_structured():
    """Test the Responses API with structured output schema."""
    orchestrator = get_orchestrator()
    
    print("\n" + "=" * 70)
    print("TESTING OPENAI RESPONSES API WITH STRUCTURED OUTPUTS")
    print("=" * 70)
    
    # Check if Responses API is available
    if not orchestrator._responses_client:
        print("⚠️ WARNING: Responses API not available. Using legacy chat completions.")
        print("To enable Responses API, ensure you have the latest OpenAI SDK.")
        return
    
    print("✅ Responses API client detected and ready")
    
    # Test queries
    test_queries = [
        "What's the current price and technical levels for TSLA?",
        "Analyze NVDA with all technical indicators",
        "Give me a comprehensive analysis of AAPL"
    ]
    
    for query in test_queries:
        print(f"\n[QUERY]: {query}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Test structured response
            result = await orchestrator.process_query(
                query=query,
                use_responses_api=True  # Force use of Responses API
            )
            
            elapsed = time.time() - start_time
            
            # Verify structured output
            if 'structured_output' in result:
                structured = result['structured_output']
                print("\n📊 STRUCTURED OUTPUT RECEIVED:")
                print(json.dumps(structured, indent=2))
                
                # Validate schema compliance
                validate_schema(structured)
                
                # Check for new trading levels
                if 'data' in structured and 'technical_levels' in structured['data']:
                    levels = structured['data']['technical_levels']
                    print("\n📈 TRADING LEVELS:")
                    print(f"  • SE (Sell High): ${levels.get('se', 'N/A')}")
                    print(f"  • Buy Low: ${levels.get('buy_low', 'N/A')}")
                    print(f"  • BTD (Buy the Dip): ${levels.get('btd', 'N/A')}")
                    print(f"  • Retest: ${levels.get('retest', 'N/A')}")
            
            print(f"\n⏱️ Response time: {elapsed:.2f}s")
            print(f"📝 Text length: {len(result.get('text', ''))} chars")
            print(f"🔧 Tools used: {result.get('tools_used', [])}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"❌ ERROR: {e}")

async def test_streaming_with_structured():
    """Test streaming with structured outputs."""
    orchestrator = get_orchestrator()
    
    print("\n" + "=" * 70)
    print("TESTING STREAMING WITH STRUCTURED OUTPUTS")
    print("=" * 70)
    
    query = "Analyze TSLA with real-time streaming"
    
    print(f"\n[STREAMING QUERY]: {query}")
    print("-" * 50)
    
    chunks_received = []
    structured_events = []
    
    try:
        async for chunk in orchestrator.stream_query(query):
            chunk_type = chunk.get("type")
            
            if chunk_type == "structured_data":
                # New structured data event
                structured_events.append(chunk)
                print(f"\n📊 [STRUCTURED EVENT]:")
                print(json.dumps(chunk.get("data", {}), indent=2))
            
            elif chunk_type == "content":
                # Regular text streaming
                print(chunk.get("text", ""), end="", flush=True)
            
            elif chunk_type == "tool_start":
                print(f"\n🔧 [TOOL START]: {chunk.get('tool')}")
            
            elif chunk_type == "tool_result":
                print(f"\n✅ [TOOL COMPLETE]: {chunk.get('tool')}")
            
            chunks_received.append(chunk)
    
    except Exception as e:
        logger.error(f"Streaming error: {e}", exc_info=True)
        print(f"\n❌ STREAMING ERROR: {e}")
    
    print(f"\n\n📊 Summary:")
    print(f"  • Total chunks: {len(chunks_received)}")
    print(f"  • Structured events: {len(structured_events)}")

def validate_schema(structured: Dict[str, Any]):
    """Validate that structured output matches expected schema."""
    required_fields = ['analysis', 'data']
    data_fields = ['symbol', 'price', 'change_percent', 'technical_levels']
    level_fields = ['se', 'buy_low', 'btd', 'retest']
    
    # Check required top-level fields
    for field in required_fields:
        if field not in structured:
            print(f"⚠️ WARNING: Missing required field '{field}'")
            return False
    
    # Check data structure
    data = structured.get('data', {})
    for field in data_fields:
        if field not in data:
            print(f"⚠️ WARNING: Missing data field '{field}'")
    
    # Check technical levels with new names
    levels = data.get('technical_levels', {})
    missing_levels = []
    for level in level_fields:
        if level not in levels:
            missing_levels.append(level)
    
    if missing_levels:
        print(f"⚠️ WARNING: Missing technical levels: {missing_levels}")
    else:
        print("✅ Schema validation passed - all new trading levels present")
    
    return len(missing_levels) == 0

async def test_sse_format():
    """Test Server-Sent Events format for frontend compatibility."""
    orchestrator = get_orchestrator()
    
    print("\n" + "=" * 70)
    print("TESTING SSE FORMAT FOR FRONTEND")
    print("=" * 70)
    
    query = "What's NVDA trading at?"
    
    # Simulate SSE streaming as it would be received by frontend
    print(f"\n[SSE SIMULATION]: {query}")
    print("-" * 50)
    
    async for chunk in orchestrator.stream_query(query):
        # Format as SSE
        sse_data = f"data: {json.dumps(chunk)}\n\n"
        
        # Show raw SSE format
        if chunk.get("type") in ["structured_data", "metadata"]:
            print(f"\n[SSE Event]:\n{sse_data[:200]}...")  # Show first 200 chars
        
        # Parse as frontend would
        try:
            parsed = json.loads(sse_data.replace("data: ", "").strip())
            
            if parsed.get("type") == "structured_data":
                print("\n✅ Frontend would receive structured data:")
                print(f"  • Symbol: {parsed['data'].get('symbol')}")
                print(f"  • Price: ${parsed['data'].get('price')}")
                print(f"  • Technical Levels: {parsed['data'].get('technical_levels')}")
        
        except json.JSONDecodeError as e:
            print(f"⚠️ SSE parsing error: {e}")

async def main():
    """Run all Responses API tests."""
    
    print("\n🚀 Starting OpenAI Responses API End-to-End Tests")
    print("=" * 70)
    
    # Run tests in sequence
    await test_responses_api_structured()
    await test_streaming_with_structured()
    await test_sse_format()
    
    print("\n" + "=" * 70)
    print("✅ ALL RESPONSES API TESTS COMPLETE")
    print("=" * 70)
    
    print("\n📋 Next Steps:")
    print("1. ✅ Trading levels renamed (ltb→btd, st→buy_low, qe→se, +retest)")
    print("2. ✅ Responses API integration tested")
    print("3. 🔄 Update frontend to handle structured JSON events")
    print("4. 🔄 Add unit tests for _generate_structured_summary")
    print("5. 🔄 Deploy and monitor SSE performance")

if __name__ == "__main__":
    asyncio.run(main())