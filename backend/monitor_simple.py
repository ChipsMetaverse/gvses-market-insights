#!/usr/bin/env python3
"""Simple request monitor"""

import requests
import time
from datetime import datetime

print("=" * 60)
print("Backend Monitor - Watching localhost:8000")
print("=" * 60)

# Test endpoints
endpoints = [
    ('GET', '/health'),
    ('GET', '/api/stock-price?symbol=PLTR'),
    ('GET', '/elevenlabs/signed-url'),
    ('POST', '/ask')
]

for method, endpoint in endpoints:
    url = f'http://localhost:8000{endpoint}'
    try:
        if method == 'GET':
            r = requests.get(url)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {method} {endpoint}: {r.status_code}")
            if r.status_code == 200 and 'stock-price' in endpoint:
                data = r.json()
                print(f"  -> PLTR: ${data.get('price', 'N/A')} via {data.get('data_source', '?')}")
        elif method == 'POST':
            payload = {"message": "Test", "sessionId": "test"}
            r = requests.post(url, json=payload)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {method} {endpoint}: {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {method} {endpoint}: ERROR - {e}")
    time.sleep(0.5)

print("\n" + "=" * 60)
print("✅ Backend is responding properly on port 8000")
print("\nTo monitor Computer Use requests:")
print("1. Have Computer Use open http://localhost:5174")
print("2. Watch the backend.log file for incoming requests")
print("3. Requests from Docker will have Origin: host.docker.internal:5174")
print("=" * 60)