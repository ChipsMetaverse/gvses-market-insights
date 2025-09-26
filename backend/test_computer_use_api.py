#!/usr/bin/env python3
"""
Test if the API is accessible from Computer Use perspective
"""

import requests

print("Testing API access from Computer Use perspective...")

# Test 1: Direct localhost (won't work from Docker)
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    print(f"✓ localhost:8000 accessible: {response.status_code}")
except Exception as e:
    print(f"✗ localhost:8000 failed: {e}")

# Test 2: host.docker.internal (should work from Docker)
try:
    response = requests.get("http://host.docker.internal:8000/health", timeout=2)
    print(f"✓ host.docker.internal:8000 accessible: {response.status_code}")
except Exception as e:
    print(f"✗ host.docker.internal:8000 failed: {e}")

# Test 3: Stock price endpoint
print("\nTesting stock price endpoint...")
try:
    response = requests.get("http://localhost:8000/api/stock-price?symbol=PLTR", timeout=5)
    print(f"✓ Stock price from localhost: {response.json()}")
except Exception as e:
    print(f"✗ Stock price from localhost failed: {e}")

try:
    response = requests.get("http://host.docker.internal:8000/api/stock-price?symbol=PLTR", timeout=5)
    print(f"✓ Stock price from host.docker.internal: {response.json()}")
except Exception as e:
    print(f"✗ Stock price from host.docker.internal failed: {e}")

# Test 4: CORS headers
print("\nTesting CORS headers...")
headers = {
    'Origin': 'http://host.docker.internal:5174',
    'Referer': 'http://host.docker.internal:5174/'
}
try:
    response = requests.get("http://localhost:8000/api/stock-price?symbol=PLTR", headers=headers, timeout=5)
    cors_headers = {k: v for k, v in response.headers.items() if 'cors' in k.lower() or 'access-control' in k.lower()}
    print(f"CORS headers from localhost: {cors_headers}")
except Exception as e:
    print(f"✗ CORS test failed: {e}")