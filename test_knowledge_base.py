#!/usr/bin/env python3
"""
Test ElevenLabs Knowledge Base API
"""

import requests
import json
from typing import Optional, Dict, Any

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
AGENT_ID = "agent_4901k2tkkq54f4mvgpndm3pgzm7g"
BASE_URL = "https://api.elevenlabs.io/v1/convai"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

def get_knowledge_base_list():
    """Get list of all knowledge base documents"""
    url = f"{BASE_URL}/knowledge-base"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def get_knowledge_base_doc(doc_id: str):
    """Get specific knowledge base document"""
    url = f"{BASE_URL}/knowledge-base/{doc_id}"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def get_agent_knowledge_base_size():
    """Get size of agent's knowledge base"""
    url = f"{BASE_URL}/agents/{AGENT_ID}/knowledge-base/size"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def upload_knowledge_base_doc(name: str, content: str, description: str = ""):
    """Upload a new knowledge base document"""
    url = f"{BASE_URL}/knowledge-base"
    
    # Create a document
    files = {
        'file': ('document.txt', content, 'text/plain')
    }
    data = {
        'name': name,
        'description': description
    }
    
    # Remove Content-Type for multipart
    upload_headers = {"xi-api-key": API_KEY}
    
    response = requests.post(url, headers=upload_headers, files=files, data=data)
    return response.status_code, response.json() if response.status_code in [200, 201] else response.text

def add_doc_to_agent(doc_id: str):
    """Add a knowledge base document to the agent"""
    url = f"{BASE_URL}/agents/{AGENT_ID}"
    
    # Get current agent config
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return response.status_code, f"Failed to get agent: {response.text}"
    
    agent_config = response.json()
    
    # Add document to knowledge base
    if 'conversation_config' not in agent_config:
        agent_config['conversation_config'] = {}
    if 'agent' not in agent_config['conversation_config']:
        agent_config['conversation_config']['agent'] = {}
    if 'prompt' not in agent_config['conversation_config']['agent']:
        agent_config['conversation_config']['agent']['prompt'] = {}
    if 'knowledge_base' not in agent_config['conversation_config']['agent']['prompt']:
        agent_config['conversation_config']['agent']['prompt']['knowledge_base'] = []
    
    agent_config['conversation_config']['agent']['prompt']['knowledge_base'].append(doc_id)
    
    # Update agent
    response = requests.patch(url, headers=headers, json=agent_config)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def main():
    print("🔍 Testing ElevenLabs Knowledge Base API")
    print("=" * 50)
    
    # 1. List existing knowledge base documents
    print("\n1. Listing knowledge base documents...")
    status, result = get_knowledge_base_list()
    print(f"   Status: {status}")
    if status == 200:
        docs = result.get('documents', []) if isinstance(result, dict) else result
        print(f"   Found {len(docs)} documents")
        for doc in docs[:5]:  # Show first 5
            print(f"   - {doc.get('name', 'Unknown')}: {doc.get('id', 'No ID')}")
    else:
        print(f"   Error: {result}")
    
    # 2. Check agent's knowledge base size
    print(f"\n2. Checking agent's knowledge base size...")
    status, result = get_agent_knowledge_base_size()
    print(f"   Status: {status}")
    print(f"   Result: {result}")
    
    # 3. Create a sample trading knowledge document
    print("\n3. Creating sample trading knowledge document...")
    
    trading_knowledge = """
# GVSES Trading Knowledge Base

## Key Trading Levels
- **LTB (Long-Term Buy)**: Deep support level, typically at 61.8% Fibonacci retracement
- **ST (Swing Trade)**: Medium-term entry point, often at 50-day moving average
- **QE (Quick Entry)**: Short-term breakout zone for momentum trades

## Market Analysis Framework
1. Check overall market conditions (SPY, QQQ)
2. Identify sector rotation patterns
3. Analyze individual stock technicals
4. Confirm with volume and momentum indicators
5. Set risk/reward ratios before entry

## Risk Management Rules
- Never risk more than 2% per trade
- Use trailing stops in trending markets
- Scale into positions in volatile conditions
- Always have an exit plan before entry

## Technical Indicators Priority
1. Moving Averages (20, 50, 200)
2. RSI for overbought/oversold
3. MACD for momentum shifts
4. Volume for confirmation
5. Support/Resistance levels

## Options Trading Guidelines
- Focus on liquid underlyings (min 1M daily volume)
- Prefer 30-45 DTE for swing trades
- Use spreads to reduce cost basis
- Monitor implied volatility rank
"""
    
    status, result = upload_knowledge_base_doc(
        name="GVSES Trading Guidelines",
        content=trading_knowledge,
        description="Core trading principles and guidelines for GVSES market analysis"
    )
    print(f"   Status: {status}")
    if status in [200, 201]:
        doc_id = result.get('id') if isinstance(result, dict) else None
        print(f"   Document created with ID: {doc_id}")
        
        if doc_id:
            # 4. Add document to agent
            print(f"\n4. Adding document to agent...")
            status, result = add_doc_to_agent(doc_id)
            print(f"   Status: {status}")
            print(f"   Result: {result[:200] if isinstance(result, str) else 'Updated successfully'}")
    else:
        print(f"   Error: {result}")
    
    print("\n✅ Knowledge Base API exploration complete!")

if __name__ == "__main__":
    main()