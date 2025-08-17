#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set tool approval policy for the get_stock_price webhook tool.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

if not API_KEY:
    print("ELEVENLABS_API_KEY not found in backend/.env")
    exit(1)

# Headers for API calls
headers = {
    'xi-api-key': API_KEY,
    'Content-Type': 'application/json'
}

# First, let's get the agent details to find any MCP server config
print(f"Fetching agent details for {AGENT_ID}...")
agent_response = requests.get(
    f'https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}',
    headers={'xi-api-key': API_KEY}
)

if agent_response.status_code == 200:
    agent_data = agent_response.json()
    print(f"Agent found: {agent_data.get('name', 'Unknown')}")
    
    # Check for MCP servers in the agent config
    mcp_server_ids = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {}).get('mcp_server_ids', [])
    if mcp_server_ids:
        print(f"Found MCP servers: {mcp_server_ids}")
        
        # For each MCP server, set tool approval policy
        for mcp_server_id in mcp_server_ids:
            print(f"\nSetting approval policy for MCP server: {mcp_server_id}")
            
            # Create tool approval for get_stock_price
            approval_response = requests.post(
                f'https://api.elevenlabs.io/v1/convai/mcp-servers/{mcp_server_id}/tool-approvals',
                headers=headers,
                json={
                    "tool_name": "get_stock_price",
                    "description": "Auto-approved stock price fetching tool",
                    "approval_policy": "auto_approved"
                }
            )
            
            if approval_response.status_code == 200:
                print(f"Tool approval set successfully for {mcp_server_id}")
            else:
                print(f"Failed to set approval: {approval_response.status_code}")
                print(approval_response.text)
    else:
        print("\nNo MCP servers found in agent config.")
        print("Note: Webhook tools don't use MCP servers, they have their own approval settings.")
        print("\nFor webhook tools, you need to:")
        print("1. Go to the ElevenLabs dashboard")
        print("2. Navigate to your agent's Tools tab")
        print("3. Find 'get_stock_price' tool")
        print("4. Change approval from 'Always Ask' to 'Never Ask'")
        print("\nThis cannot be done via API for webhook tools.")
else:
    print(f"Failed to fetch agent: {agent_response.status_code}")
    print(agent_response.text)