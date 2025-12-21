#!/usr/bin/env python3
"""
Test script to verify anyOf/allOf/oneOf schema sanitization.
"""

import sys
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

from services.openai_tool_mapper import OpenAIToolMapper

def test_anyof_sanitization():
    """Test that anyOf at top level is properly flattened"""
    mapper = OpenAIToolMapper()
    
    # Simulate a problematic MCP tool with anyOf at top level
    mcp_tool_anyof = {
        "name": "test_tool_anyof",
        "description": "Test tool with anyOf",
        "inputSchema": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "properties": {
                        "param2": {"type": "number"}
                    }
                }
            ]
        }
    }
    
    result = mapper._convert_mcp_to_openai_tool(mcp_tool_anyof)
    print("✅ anyOf test:")
    print(f"   Tool name: {result['function']['name']}")
    print(f"   Parameters type: {result['function']['parameters']['type']}")
    print(f"   Parameters: {result['function']['parameters']}")
    assert "anyOf" not in str(result), "anyOf should be removed"
    assert result['function']['parameters']['type'] == 'object', "Should be flattened to object"
    print("   ✓ anyOf successfully flattened\n")

def test_allof_sanitization():
    """Test that allOf at top level is properly merged"""
    mapper = OpenAIToolMapper()
    
    mcp_tool_allof = {
        "name": "test_tool_allof",
        "description": "Test tool with allOf",
        "inputSchema": {
            "allOf": [
                {
                    "type": "object",
                    "properties": {
                        "base_prop": {"type": "string"}
                    },
                    "required": ["base_prop"]
                },
                {
                    "type": "object",
                    "properties": {
                        "extra_prop": {"type": "number"}
                    },
                    "required": ["extra_prop"]
                }
            ]
        }
    }
    
    result = mapper._convert_mcp_to_openai_tool(mcp_tool_allof)
    print("✅ allOf test:")
    print(f"   Tool name: {result['function']['name']}")
    print(f"   Parameters: {result['function']['parameters']}")
    assert "allOf" not in str(result), "allOf should be removed"
    assert "base_prop" in result['function']['parameters']['properties'], "Should have base_prop"
    assert "extra_prop" in result['function']['parameters']['properties'], "Should have extra_prop"
    print("   ✓ allOf successfully merged\n")

def test_oneof_sanitization():
    """Test that oneOf at top level is properly flattened"""
    mapper = OpenAIToolMapper()
    
    mcp_tool_oneof = {
        "name": "test_tool_oneof",
        "description": "Test tool with oneOf",
        "inputSchema": {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "option1": {"type": "string"}
                    }
                },
                {
                    "type": "object",
                    "properties": {
                        "option2": {"type": "boolean"}
                    }
                }
            ]
        }
    }
    
    result = mapper._convert_mcp_to_openai_tool(mcp_tool_oneof)
    print("✅ oneOf test:")
    print(f"   Tool name: {result['function']['name']}")
    print(f"   Parameters: {result['function']['parameters']}")
    assert "oneOf" not in str(result), "oneOf should be removed"
    assert result['function']['parameters']['type'] == 'object', "Should be flattened to object"
    print("   ✓ oneOf successfully flattened\n")

def test_nested_anyof_sanitization():
    """Test that anyOf in property definitions is also sanitized"""
    mapper = OpenAIToolMapper()
    
    mcp_tool_nested = {
        "name": "test_tool_nested",
        "description": "Test tool with nested anyOf",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mixed_param": {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "number"}
                    ]
                }
            }
        }
    }
    
    result = mapper._convert_mcp_to_openai_tool(mcp_tool_nested)
    print("✅ nested anyOf test:")
    print(f"   Tool name: {result['function']['name']}")
    print(f"   Parameters: {result['function']['parameters']}")
    assert "anyOf" not in str(result), "Nested anyOf should be removed"
    print("   ✓ Nested anyOf successfully handled\n")

def test_normal_schema():
    """Test that normal schemas pass through correctly"""
    mapper = OpenAIToolMapper()
    
    mcp_tool_normal = {
        "name": "test_tool_normal",
        "description": "Normal test tool",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days",
                    "default": 30
                }
            },
            "required": ["symbol"]
        }
    }
    
    result = mapper._convert_mcp_to_openai_tool(mcp_tool_normal)
    print("✅ normal schema test:")
    print(f"   Tool name: {result['function']['name']}")
    print(f"   Parameters: {result['function']['parameters']}")
    assert result['function']['parameters']['properties']['symbol']['type'] == 'string'
    assert result['function']['parameters']['properties']['days']['default'] == 30
    assert 'symbol' in result['function']['parameters']['required']
    print("   ✓ Normal schema preserved correctly\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Schema Sanitization for Claude API Compatibility")
    print("=" * 60)
    print()
    
    try:
        test_anyof_sanitization()
        test_allof_sanitization()
        test_oneof_sanitization()
        test_nested_anyof_sanitization()
        test_normal_schema()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe schema sanitization is working correctly!")
        print("MCP tools with anyOf/allOf/oneOf will now be compatible with Claude API.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)





























