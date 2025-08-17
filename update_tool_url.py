#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update the ElevenLabs tool to use the correct public URL.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
TOOL_ID = 'tool_3301k2v1d9gsed6tw97jsrpj84as'  # From the screenshot

if not API_KEY:
    print("ELEVENLABS_API_KEY not found in backend/.env")
    exit(1)

# Headers for API calls
headers = {
    'xi-api-key': API_KEY,
    'Content-Type': 'application/json'
}

print(f"Updating tool {TOOL_ID} with public URL...")

# Update the tool with the correct URL
update_response = requests.patch(
    f'https://api.elevenlabs.io/v1/convai/tools/{TOOL_ID}',
    headers=headers,
    json={
        "tool_config": {
            "type": "webhook",
            "name": "get_stock_price",
            "description": "Fetches the current stock price and market data for a given stock symbol",
            "api_schema": {
                "url": "https://gvses-backend.loca.lt/api/stock-price",
                "method": "GET",
                "query_params_schema": [
                    {
                        "id": "symbol",
                        "type": "string",
                        "value_type": "llm_prompt",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)",
                        "required": True
                    }
                ]
            },
            "response_timeout_secs": 20
        }
    }
)

if update_response.status_code == 200:
    print("✅ Tool URL updated successfully!")
    print("The tool now points to: https://gvses-backend.loca.lt/api/stock-price")
else:
    print(f"❌ Failed to update tool: {update_response.status_code}")
    print(update_response.text)