#!/usr/bin/env python3
"""Trigger OpenAI relay initialization on production."""

import requests
import json

# First check health
print("1. Checking health endpoint...")
health_response = requests.get("https://gvses-market-insights.fly.dev/health")
health_data = health_response.json()
print(f"   OpenAI relay ready: {health_data.get('openai_relay_ready', False)}")

# Try to access a market endpoint to trigger service initialization
print("\n2. Triggering service initialization via market endpoint...")
try:
    market_response = requests.get(
        "https://gvses-market-insights.fly.dev/api/stock-price",
        params={"symbol": "AAPL"}
    )
    print(f"   Market endpoint status: {market_response.status_code}")
except Exception as e:
    print(f"   Market endpoint error: {e}")

# Check health again
print("\n3. Checking health endpoint again...")
health_response2 = requests.get("https://gvses-market-insights.fly.dev/health")
health_data2 = health_response2.json()
print(f"   OpenAI relay ready: {health_data2.get('openai_relay_ready', False)}")
print(f"   Service initialized: {health_data2.get('service_initialized', False)}")
print(f"   Service mode: {health_data2.get('service_mode', 'unknown')}")

# Check OpenAI relay details
openai_relay = health_data2.get('openai_relay', {})
if openai_relay:
    print(f"\n   OpenAI Relay Details:")
    print(f"   - Active: {openai_relay.get('active', False)}")
    print(f"   - Reason: {openai_relay.get('reason', 'unknown')}")
    if openai_relay.get('active'):
        print(f"   - Sessions: {openai_relay.get('sessions', 0)}")
        print(f"   - Tool mapper initialized: {openai_relay.get('tool_mapper_initialized', False)}")
        print(f"   - Enhanced training loaded: {openai_relay.get('enhanced_training_loaded', False)}")