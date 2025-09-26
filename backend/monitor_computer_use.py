#!/usr/bin/env python3
"""Monitor for Computer Use specific requests"""

import subprocess
import time
from datetime import datetime

print("=" * 80)
print("🤖 Computer Use Request Monitor")
print("=" * 80)
print("Watching for requests from Docker container (host.docker.internal)")
print("Expected patterns:")
print("  • Origin: host.docker.internal:5174")
print("  • OPTIONS preflight requests")
print("  • GET/POST to API endpoints")
print("-" * 80)

# Tail the log file and filter for relevant patterns
cmd = [
    "tail", "-F", "backend.log"
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

try:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Monitoring started...")
    print("Waiting for Computer Use to connect...\n")
    
    for line in process.stdout:
        # Look for Computer Use specific patterns
        if any(pattern in line for pattern in [
            "host.docker.internal",
            "OPTIONS",
            "/elevenlabs/signed-url",
            "/ask",
            "Origin:",
            "CORS",
            "Access-Control"
        ]):
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Highlight Computer Use requests
            if "host.docker.internal" in line:
                print(f"[{timestamp}] 🎯 COMPUTER USE REQUEST:")
                print(f"  {line.strip()}")
            elif "OPTIONS" in line:
                print(f"[{timestamp}] 🔄 CORS Preflight:")
                print(f"  {line.strip()}")
            else:
                print(f"[{timestamp}] {line.strip()}")
                
except KeyboardInterrupt:
    print("\n\nMonitoring stopped.")
finally:
    process.terminate()