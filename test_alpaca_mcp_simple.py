#!/usr/bin/env python3
"""
Simple test for Alpaca MCP Server
"""

import os
import json
import subprocess
import time

def test_alpaca_mcp():
    """Test the Alpaca MCP server can start."""
    print("Testing Alpaca MCP Server startup...")
    
    # Set environment variables
    env = os.environ.copy()
    env['ALPACA_API_KEY'] = 'PKM2U9W8XB8D0EUP1Q38'
    env['ALPACA_SECRET_KEY'] = 'HdSPzEKEvMEcgUqKcNModn1nXaTCyDOK4Mr5mW3t'
    env['ALPACA_BASE_URL'] = 'https://paper-api.alpaca.markets'
    
    try:
        # Start the server
        proc = subprocess.Popen(
            ['python3', 'alpaca-mcp-server/server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Give it time to start
        time.sleep(2)
        
        # Check if process is still running
        if proc.poll() is None:
            print("✅ Alpaca MCP Server started successfully!")
            
            # Send a list tools request via stdin
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            proc.stdin.write(json.dumps(request) + '\n')
            proc.stdin.flush()
            
            # Read response
            response_line = proc.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                if 'result' in response and 'tools' in response['result']:
                    print(f"✅ Server has {len(response['result']['tools'])} tools available")
                    for tool in response['result']['tools'][:3]:
                        print(f"  - {tool['name']}")
            
            # Terminate the process
            proc.terminate()
            proc.wait()
        else:
            # Process died, check stderr
            stderr = proc.stderr.read()
            print(f"❌ Server failed to start. Error:\n{stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpaca_mcp()