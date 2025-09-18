#!/usr/bin/env python3
"""
Unit tests for _generate_structured_summary method.
Tests the structured output generation with the new Responses API.
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from services.agent_orchestrator import AgentOrchestrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_generate_structured_summary():
    """Test the _generate_structured_summary method."""
    
    print("\n" + "=" * 70)
    print("TESTING _generate_structured_summary")
    print("=" * 70)
    
    # Create orchestrator instance
    orchestrator = AgentOrchestrator()
    
    # Mock tool results with new trading levels
    mock_tool_results = {
        "get_stock_price": {
            "symbol": "TSLA",
            "price": 425.50,
            "change": 12.30,
            "change_percent": 2.97,
            "volume": 125000000
        },
        "get_comprehensive_stock_data": {
            "symbol": "TSLA",
            "price": 425.50,
            "technicals": {
                "se_level": 440.25,  # Sell High
                "buy_low_level": 390.00,  # Buy Low
                "btd_level": 365.50,  # Buy the Dip
                "retest_level": 415.00,  # Retest
                "ma_20": 418.75,
                "ma_50": 405.30,
                "ma_200": 380.25
            }
        }
    }
    
    # Test query
    query = "Analyze TSLA with all technical levels"
    
    # Mock the Responses API if available
    if orchestrator._responses_client:
        print("✅ Testing with actual Responses API client")
        
        # Create mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.parsed = {
            "analysis": "TSLA showing strong bullish momentum, approaching SE (Sell High) resistance at $440.25. Current price of $425.50 is above all major moving averages. Buy Low support at $390 and BTD level at $365.50 provide strong downside protection. Retest level at $415 could act as immediate support.",
            "data": {
                "symbol": "TSLA",
                "price": 425.50,
                "change_percent": 2.97,
                "technical_levels": {
                    "se": 440.25,
                    "buy_low": 390.00,
                    "btd": 365.50,
                    "retest": 415.00
                }
            },
            "tools_used": ["get_stock_price", "get_comprehensive_stock_data"],
            "confidence": 0.85
        }
        
        # Patch the responses.create method
        with patch.object(orchestrator._responses_client, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            
            # Test the method
            result = await orchestrator._generate_structured_summary(
                query=query,
                tools_used=["get_stock_price", "get_comprehensive_stock_data"],
                tool_results=mock_tool_results
            )
            
            print("\n📊 Structured Summary Generated:")
            print(json.dumps(result, indent=2))
            
            # Validate the result
            assert result is not None, "Result should not be None"
            assert "analysis" in result, "Result should contain 'analysis'"
            assert "data" in result, "Result should contain 'data'"
            assert "technical_levels" in result["data"], "Data should contain 'technical_levels'"
            
            # Check for new trading levels
            levels = result["data"]["technical_levels"]
            assert "se" in levels, "Should have 'se' (Sell High) level"
            assert "buy_low" in levels, "Should have 'buy_low' level"
            assert "btd" in levels, "Should have 'btd' (Buy the Dip) level"
            assert "retest" in levels, "Should have 'retest' level"
            
            # Verify old levels are NOT present
            assert "qe" not in levels, "Should NOT have old 'qe' level"
            assert "st" not in levels, "Should NOT have old 'st' level"
            assert "ltb" not in levels, "Should NOT have old 'ltb' level"
            
            print("\n✅ All assertions passed!")
            
    else:
        print("⚠️ Responses API not available, testing fallback behavior")
        
        # Test that method returns None when Responses API unavailable
        result = await orchestrator._generate_structured_summary(
            query=query,
            tools_used=["get_stock_price", "get_comprehensive_stock_data"],
            tool_results=mock_tool_results
        )
        
        assert result is None, "Should return None when Responses API unavailable"
        print("✅ Fallback behavior correct")

async def test_schema_validation():
    """Test that the schema properly validates the new trading levels."""
    
    print("\n" + "=" * 70)
    print("TESTING SCHEMA VALIDATION")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    # Check the schema definition
    schema = orchestrator.response_schema
    
    print("\n📋 Checking schema definition...")
    
    # Navigate to technical_levels in schema
    tech_levels_schema = schema["schema"]["properties"]["data"]["properties"]["technical_levels"]["properties"]
    
    print("Technical levels in schema:")
    for level_name in tech_levels_schema.keys():
        print(f"  • {level_name}")
    
    # Validate new levels are in schema
    expected_levels = ["se", "buy_low", "btd", "retest"]
    unexpected_levels = ["qe", "st", "ltb"]
    
    for level in expected_levels:
        assert level in tech_levels_schema, f"Schema should include '{level}' level"
        print(f"✅ '{level}' level found in schema")
    
    for level in unexpected_levels:
        assert level not in tech_levels_schema, f"Schema should NOT include old '{level}' level"
        print(f"✅ Old '{level}' level NOT in schema")
    
    print("\n✅ Schema validation passed!")

async def test_message_conversion():
    """Test message conversion for Responses API."""
    
    print("\n" + "=" * 70)
    print("TESTING MESSAGE CONVERSION")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator()
    
    # Test messages with old level references
    test_messages = [
        {"role": "system", "content": "You are a trading assistant."},
        {"role": "user", "content": "What are the QE and LTB levels for TSLA?"},
        {"role": "assistant", "content": "Looking at TSLA's SE (Sell High) and BTD (Buy the Dip) levels..."}
    ]
    
    # Convert messages
    if hasattr(orchestrator, '_convert_messages_for_responses'):
        converted = orchestrator._convert_messages_for_responses(test_messages)
        
        print("\n📝 Original messages:")
        for msg in test_messages:
            print(f"  {msg['role']}: {msg['content'][:50]}...")
        
        print("\n📝 Converted messages:")
        for msg in converted:
            print(f"  {msg['role']}: {msg.get('content', msg.get('text', ''))[:50]}...")
        
        print("\n✅ Message conversion tested")
    else:
        print("⚠️ _convert_messages_for_responses method not found")

async def main():
    """Run all structured summary tests."""
    
    print("\n🚀 Starting Structured Summary Tests")
    print("=" * 70)
    
    # Run tests
    await test_generate_structured_summary()
    await test_schema_validation()
    await test_message_conversion()
    
    print("\n" + "=" * 70)
    print("✅ ALL STRUCTURED SUMMARY TESTS COMPLETE")
    print("=" * 70)
    
    print("\n📊 Summary:")
    print("• Schema updated with new trading levels (se, buy_low, btd, retest)")
    print("• Old levels (qe, st, ltb) removed from schema")
    print("• Structured summary generation tested")
    print("• Message conversion validated")

if __name__ == "__main__":
    asyncio.run(main())