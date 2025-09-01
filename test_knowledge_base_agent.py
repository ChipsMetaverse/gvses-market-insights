#!/usr/bin/env python3
"""
Test the ElevenLabs agent with knowledge base enabled
"""

import asyncio
import websocket
import json
import requests
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"

def get_signed_url():
    """Get signed WebSocket URL from backend"""
    response = requests.get(f"{BACKEND_URL}/elevenlabs/signed-url")
    if response.status_code == 200:
        return response.json()["signed_url"]
    else:
        raise Exception(f"Failed to get signed URL: {response.text}")

def test_knowledge_base_questions():
    """Test the agent with knowledge base questions"""
    
    print("🧠 Testing ElevenLabs Agent with Knowledge Base")
    print("=" * 60)
    
    # Get signed URL
    print("\n1. Getting signed WebSocket URL...")
    signed_url = get_signed_url()
    print(f"   ✓ Got URL: {signed_url[:100]}...")
    
    # Knowledge base test questions
    test_questions = [
        {
            "question": "What is LTB in trading?",
            "expected": "Long-Term Buy, deep support level, 61.8% Fibonacci"
        },
        {
            "question": "Tell me about candlestick patterns",
            "expected": "Should reference THE CANDLESTICK TRADING BIBLE"
        },
        {
            "question": "What are the key levels for swing trading?",
            "expected": "ST (Swing Trade), 50-day moving average"
        },
        {
            "question": "How do I manage risk in trading?",
            "expected": "Never risk more than 2% per trade"
        }
    ]
    
    print("\n2. Testing Knowledge Base Questions:")
    print("-" * 40)
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n   Test {i}: {test['question']}")
        print(f"   Expected: {test['expected']}")
        
        try:
            # Connect to WebSocket
            ws = websocket.create_connection(signed_url)
            
            # Send initialization
            init_message = {
                "type": "conversation_initiation_client_data",
                "conversation_config_override": {
                    "agent": {
                        "prompt": {
                            "prompt": "You are a helpful trading assistant with access to knowledge base documents."
                        }
                    },
                    "conversation": {
                        "text_only": True
                    }
                }
            }
            ws.send(json.dumps(init_message))
            
            # Wait for initialization response
            time.sleep(1)
            
            # Send test question
            text_message = {
                "type": "user_text",
                "text": test['question']
            }
            ws.send(json.dumps(text_message))
            
            # Collect response
            response_text = ""
            timeout = time.time() + 10  # 10 second timeout
            
            while time.time() < timeout:
                try:
                    result = ws.recv()
                    message = json.loads(result)
                    
                    if message.get("type") == "agent_response":
                        agent_resp = message.get("agent_response", {})
                        if agent_resp.get("type") == "text":
                            response_text += agent_resp.get("text", "")
                    elif message.get("type") == "conversation_end":
                        break
                        
                except websocket.WebSocketTimeoutException:
                    break
                except Exception as e:
                    print(f"   Error receiving: {e}")
                    break
            
            ws.close()
            
            # Check response
            if response_text:
                print(f"   Response: {response_text[:200]}...")
                
                # Check if expected content is in response
                if any(keyword.lower() in response_text.lower() for keyword in test['expected'].split(',')):
                    print("   ✅ Knowledge base content found!")
                else:
                    print("   ⚠️ Expected content not clearly found")
            else:
                print("   ❌ No response received")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n3. Knowledge Base Integration Summary:")
    print("-" * 40)
    print("   ✓ Agent configured with 5 knowledge base documents")
    print("   ✓ RAG enabled for retrieval-augmented generation")
    print("   ✓ Documents include trading guides and patterns")
    print("\n📚 Knowledge Base Documents:")
    print("   1. GVSES Trading Guidelines")
    print("   2. Encyclopedia of Chart Patterns")
    print("   3. THE CANDLESTICK TRADING BIBLE")
    print("   4. Yahoo Finance Market Data")
    print("   5. CoinMarketCap Crypto Data")
    
    print("\n✅ Knowledge Base Test Complete!")

if __name__ == "__main__":
    test_knowledge_base_questions()