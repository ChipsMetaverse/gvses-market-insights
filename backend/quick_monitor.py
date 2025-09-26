#!/usr/bin/env python3
"""Quick backend monitor to see incoming requests"""

import requests
import time
from datetime import datetime

def monitor():
    print("🔍 Monitoring backend on http://localhost:8000")
    print("=" * 60)
    
    # Test health endpoint
    try:
        resp = requests.get('http://localhost:8000/health')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Health: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Data: {resp.json()}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("-" * 60)
    
    # Test stock price
    try:
        resp = requests.get('http://localhost:8000/api/stock-price?symbol=PLTR')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] PLTR Price: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Price: ${data.get('price', 'N/A')}")
            print(f"  Source: {data.get('data_source', 'unknown')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("-" * 60)
    
    # Test CORS preflight
    try:
        headers = {
            'Origin': 'http://host.docker.internal:5174',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'content-type',
        }
        resp = requests.options('http://localhost:8000/api/stock-price', headers=headers)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] CORS Preflight: {resp.status_code}")
        print(f"  Headers: {dict(resp.headers)}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("=" * 60)
    print("\n✅ Monitoring complete. Backend is responding on port 8000.")
    print("\nNOTE: To see live requests from Computer Use:")
    print("1. Have Computer Use navigate to http://localhost:5174")
    print("2. Click 'Click mic to start' in Voice Assistant panel")
    print("3. Requests will appear in backend logs")

if __name__ == "__main__":
    monitor()