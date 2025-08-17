#!/usr/bin/env python3
"""
Expose the backend API using ngrok for webhook access.
"""

from pyngrok import ngrok
import time
import sys

# Start ngrok tunnel for port 8000
public_url = ngrok.connect(8000)

print(f"🌐 Backend exposed at: {public_url}")
print(f"📡 Stock price endpoint: {public_url}/api/stock-price")
print(f"\n✅ Use this URL for ElevenLabs webhook tools")
print(f"\nPress Ctrl+C to stop the tunnel...")

try:
    # Keep the tunnel open
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Closing tunnel...")
    ngrok.disconnect(public_url)
    ngrok.kill()
    sys.exit(0)