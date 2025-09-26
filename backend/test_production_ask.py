#!/usr/bin/env python3
import os
import sys
import json

# Set environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

print("Starting test...")
print(f"OPENAI_API_KEY set: {bool(os.environ.get('OPENAI_API_KEY'))}")
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

try:
    # Check if knowledge base exists
    kb_path = "/app/backend/knowledge_base_embedded.json"
    if os.path.exists(kb_path):
        print(f"✓ Knowledge base exists at {kb_path}")
        with open(kb_path, 'r') as f:
            data = json.load(f)
            print(f"✓ Knowledge base loaded: {len(data.get('embeddings', []))} embeddings")
    else:
        print(f"✗ Knowledge base NOT found at {kb_path}")
    
    # Try to import and initialize orchestrator
    print("\nInitializing orchestrator...")
    from services.agent_orchestrator import get_orchestrator
    
    orchestrator = get_orchestrator()
    print("✓ Orchestrator initialized successfully")
    
    # Try to process a query
    print("\nProcessing test query...")
    response = orchestrator.process_query("What are support and resistance levels?")
    print("✓ Query processed successfully")
    print(f"Response preview: {response[:200]}...")
    
except Exception as e:
    print(f"\n✗ Error occurred: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()