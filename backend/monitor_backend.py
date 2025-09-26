#!/usr/bin/env python3
"""
Real-time backend monitoring with detailed request/response logging
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import httpx
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.layout import Layout
from rich.text import Text

console = Console()

class BackendMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.request_count = 0
        self.last_requests = []
        
    async def test_endpoint(self, method: str, path: str, data: Dict[str, Any] = None):
        """Test an endpoint and return formatted result"""
        self.request_count += 1
        url = f"{self.base_url}{path}"
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url)
                else:
                    response = await client.post(url, json=data)
                
                elapsed = (time.time() - start_time) * 1000  # ms
                
                # Format response
                result = {
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "method": method,
                    "path": path,
                    "status": response.status_code,
                    "elapsed_ms": f"{elapsed:.1f}",
                    "request": data if data else None,
                    "response": response.json() if response.status_code == 200 else response.text
                }
                
                # Keep last 10 requests
                self.last_requests.append(result)
                if len(self.last_requests) > 10:
                    self.last_requests.pop(0)
                    
                return result
                
        except Exception as e:
            result = {
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "method": method,
                "path": path,
                "status": "ERROR",
                "elapsed_ms": f"{(time.time() - start_time) * 1000:.1f}",
                "error": str(e)
            }
            self.last_requests.append(result)
            if len(self.last_requests) > 10:
                self.last_requests.pop(0)
            return result
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """Format a response for display"""
        lines = []
        
        # Header
        status_color = "green" if result.get("status") == 200 else "red"
        lines.append(f"[bold {status_color}]{result['method']} {result['path']} → {result['status']} ({result['elapsed_ms']}ms)[/]")
        
        # Request body if present
        if result.get("request"):
            lines.append("\n[cyan]Request:[/]")
            lines.append(json.dumps(result["request"], indent=2))
        
        # Response
        if result.get("response"):
            lines.append("\n[yellow]Response:[/]")
            if isinstance(result["response"], dict):
                # Special handling for agent responses
                resp = result["response"]
                
                # Show text response
                if "text" in resp:
                    lines.append(f"[green]Text:[/] {resp['text'][:200]}...")
                
                # Show tools used
                if "tools_used" in resp and resp["tools_used"]:
                    lines.append(f"[magenta]Tools:[/] {', '.join(resp['tools_used'])}")
                
                # Show chart commands
                if "chart_commands" in resp:
                    lines.append(f"[blue]Chart Commands:[/] {resp['chart_commands']}")
                
                # Show data keys
                if "data" in resp and resp["data"]:
                    data_keys = list(resp["data"].keys()) if isinstance(resp["data"], dict) else []
                    if data_keys:
                        lines.append(f"[cyan]Data Keys:[/] {', '.join(data_keys)}")
                        
                        # Show sample data for each tool
                        for key in data_keys[:2]:  # Show first 2 tools
                            tool_data = resp["data"][key]
                            if isinstance(tool_data, dict):
                                sample = {k: v for k, v in list(tool_data.items())[:5]}
                                lines.append(f"  {key}: {json.dumps(sample, indent=2)[:200]}...")
            else:
                lines.append(str(result["response"])[:500])
        
        # Error if present
        if result.get("error"):
            lines.append(f"\n[red]Error: {result['error']}[/]")
        
        return "\n".join(lines)

async def monitor_loop():
    """Main monitoring loop"""
    monitor = BackendMonitor()
    
    console.print(Panel("[bold green]Backend Monitor Started[/]\nMonitoring http://localhost:8000", title="Status"))
    console.print("[yellow]Press Ctrl+C to stop[/]\n")
    
    # Test queries
    test_queries = [
        ("GET", "/health", None),
        ("POST", "/api/agent/orchestrate", {"query": "What's the current price of AAPL?"}),
        ("POST", "/api/agent/orchestrate", {"query": "Switch the chart to PLTR and give me analysis"}),
        ("POST", "/api/agent/orchestrate", {"query": "Show me TSLA with technical indicators"}),
        ("GET", "/api/stock-price?symbol=NVDA", None),
    ]
    
    query_index = 0
    
    while True:
        try:
            # Rotate through test queries
            method, path, data = test_queries[query_index % len(test_queries)]
            
            # Execute request
            result = await monitor.test_endpoint(method, path, data)
            
            # Clear screen and show result
            console.clear()
            console.print(Panel(f"[bold]Request #{monitor.request_count}[/]", title="Backend Monitor"))
            
            # Show current request
            console.print(Panel(monitor.format_response(result), title="Current Request", border_style="blue"))
            
            # Show recent history
            if len(monitor.last_requests) > 1:
                history_text = []
                for req in monitor.last_requests[-5:]:
                    status_icon = "✅" if req.get("status") == 200 else "❌"
                    history_text.append(
                        f"{req['timestamp']} {status_icon} {req['method']} {req['path']} "
                        f"({req['elapsed_ms']}ms)"
                    )
                console.print(Panel("\n".join(history_text), title="Recent Requests", border_style="dim"))
            
            query_index += 1
            await asyncio.sleep(3)  # Wait 3 seconds between requests
            
        except KeyboardInterrupt:
            console.print("\n[red]Monitoring stopped[/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_loop())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/]")
