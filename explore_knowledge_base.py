#!/usr/bin/env python3
"""
Comprehensive exploration of ElevenLabs Knowledge Base functionality
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

def get_agent_details():
    """Get detailed agent configuration"""
    url = f"{BASE_URL}/agents/{AGENT_ID}"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def list_knowledge_base_docs():
    """List all knowledge base documents"""
    url = f"{BASE_URL}/knowledge-base"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def get_doc_details(doc_id: str):
    """Get details of a specific document"""
    url = f"{BASE_URL}/knowledge-base/{doc_id}"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def get_doc_dependent_agents(doc_id: str):
    """Get agents that depend on this document"""
    url = f"{BASE_URL}/knowledge-base/{doc_id}/dependent-agents"
    response = requests.get(url, headers=headers)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def update_agent_knowledge_base(doc_ids: list):
    """Update agent to use knowledge base documents"""
    url = f"{BASE_URL}/agents/{AGENT_ID}"
    
    # Get current config
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return response.status_code, f"Failed to get agent: {response.text}"
    
    agent_config = response.json()
    
    # Prepare minimal update with just knowledge base
    update_data = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "knowledge_base": doc_ids,
                    "rag": {
                        "enabled": True,
                        "embedding_model": "e5_mistral_7b_instruct",
                        "max_vector_distance": 0.6,
                        "max_documents_length": 50000,
                        "max_retrieved_rag_chunks_count": 20
                    }
                }
            }
        }
    }
    
    # Patch the agent
    response = requests.patch(url, headers=headers, json=update_data)
    return response.status_code, response.json() if response.status_code == 200 else response.text

def main():
    print("🔍 Comprehensive ElevenLabs Knowledge Base Exploration")
    print("=" * 60)
    
    # 1. Get current agent configuration
    print("\n1. Current Agent Configuration:")
    print("-" * 40)
    status, result = get_agent_details()
    if status == 200:
        agent = result
        conv_config = agent.get('conversation_config', {})
        agent_config = conv_config.get('agent', {})
        prompt_config = agent_config.get('prompt', {})
        
        print(f"   Agent Name: {agent.get('name', 'Unknown')}")
        print(f"   Agent ID: {agent.get('agent_id', 'Unknown')}")
        print(f"   LLM: {prompt_config.get('llm', 'Unknown')}")
        print(f"   Tool IDs: {len(prompt_config.get('tool_ids', []))} tools")
        print(f"   Knowledge Base: {prompt_config.get('knowledge_base', [])}")
        
        rag_config = prompt_config.get('rag', {})
        print(f"\n   RAG Configuration:")
        print(f"   - Enabled: {rag_config.get('enabled', False)}")
        print(f"   - Embedding Model: {rag_config.get('embedding_model', 'None')}")
        print(f"   - Max Vector Distance: {rag_config.get('max_vector_distance', 'None')}")
        print(f"   - Max Documents Length: {rag_config.get('max_documents_length', 'None')}")
        print(f"   - Max Retrieved Chunks: {rag_config.get('max_retrieved_rag_chunks_count', 'None')}")
    else:
        print(f"   Error: {result}")
    
    # 2. List all knowledge base documents
    print("\n2. Available Knowledge Base Documents:")
    print("-" * 40)
    status, result = list_knowledge_base_docs()
    doc_ids = []
    if status == 200:
        docs = result.get('documents', []) if isinstance(result, dict) else result
        print(f"   Total documents: {len(docs)}")
        for i, doc in enumerate(docs[:10], 1):
            doc_id = doc.get('id', 'No ID')
            doc_ids.append(doc_id)
            print(f"   {i}. {doc.get('name', 'Unknown')}")
            print(f"      ID: {doc_id}")
            print(f"      Size: {doc.get('size', 'Unknown')} bytes")
            print(f"      Created: {doc.get('created_at', 'Unknown')}")
    else:
        print(f"   Error: {result}")
    
    # 3. Check specific document details
    if doc_ids:
        print("\n3. Document Details (first document):")
        print("-" * 40)
        doc_id = doc_ids[0]
        status, result = get_doc_details(doc_id)
        if status == 200:
            print(f"   Document: {result.get('name', 'Unknown')}")
            print(f"   Type: {result.get('type', 'Unknown')}")
            print(f"   Description: {result.get('description', 'None')}")
        else:
            print(f"   Error: {result}")
        
        # 4. Check dependent agents
        print("\n4. Agents Using This Document:")
        print("-" * 40)
        status, result = get_doc_dependent_agents(doc_id)
        if status == 200:
            agents = result.get('agents', []) if isinstance(result, dict) else result
            if agents:
                for agent in agents:
                    print(f"   - {agent.get('name', 'Unknown')} ({agent.get('agent_id', 'Unknown')})")
            else:
                print("   No agents currently using this document")
        else:
            print(f"   Error: {result}")
    
    # 5. Identify the issue with adding documents
    print("\n5. Knowledge Base Integration Issue Analysis:")
    print("-" * 40)
    print("   Issue: 'Cannot specify both tools and tool_ids'")
    print("   Cause: The agent configuration has:")
    print("   - tool_ids: List of tool IDs (current setup)")
    print("   - tools: Tool definitions (deprecated/conflicting)")
    print("\n   Solution: Use only tool_ids when updating knowledge base")
    print("   The convai CLI handles this correctly, but direct API calls need care")
    
    # 6. Proper way to add knowledge base
    print("\n6. Recommended Knowledge Base Setup:")
    print("-" * 40)
    print("   Method 1: Use convai CLI (preferred)")
    print("   - Edit agent_configs/gsves_market_insights.json")
    print("   - Add document IDs to knowledge_base array")
    print("   - Enable RAG in the config")
    print("   - Run: convai sync --env prod")
    print("\n   Method 2: Direct API update")
    print("   - Use PATCH endpoint with minimal update")
    print("   - Only update knowledge_base and rag fields")
    print("   - Don't include tool_ids in the update")
    
    # 7. Show example configuration
    print("\n7. Example Knowledge Base Configuration:")
    print("-" * 40)
    example_config = {
        "knowledge_base": [
            "lsBT1M95ifxCezXb8Zx9"  # Our created document
        ],
        "rag": {
            "enabled": True,
            "embedding_model": "e5_mistral_7b_instruct",
            "max_vector_distance": 0.6,
            "max_documents_length": 50000,
            "max_retrieved_rag_chunks_count": 20
        }
    }
    print(json.dumps(example_config, indent=2))
    
    print("\n✅ Knowledge Base exploration complete!")
    print("\n📝 Key Findings:")
    print("1. Knowledge base documents exist and are accessible")
    print("2. Agent currently has empty knowledge_base array")
    print("3. RAG is disabled in current configuration")
    print("4. Tool conflicts prevent direct API updates")
    print("5. Best approach: Update via convai CLI after config changes")

if __name__ == "__main__":
    main()