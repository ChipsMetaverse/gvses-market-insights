#!/usr/bin/env python3
"""
Debug Vision Tool - Computer Use Integration for Testing Assistance

This tool uses OpenAI's Computer Use Preview model to:
1. Take screenshots of your current screen/browser
2. Analyze what you're seeing during testing
3. Help debug issues by understanding the visual state
4. Provide real-time assistance based on what's displayed

Usage:
    python debug_vision_tool.py --screenshot  # Take a screenshot and analyze
    python debug_vision_tool.py --help-debug "describe the issue"  # Debug with context
    python debug_vision_tool.py --monitor     # Continuous monitoring mode
"""

import os
import sys
import time
import base64
import argparse
import subprocess
from typing import Optional, Dict, Any
from openai import OpenAI

class DebugVisionTool:
    def __init__(self):
        self.client = OpenAI()
        self.model = "computer-use-preview"
        
    def take_screenshot_macos(self) -> bytes:
        """Take a screenshot on macOS using screencapture."""
        try:
            # Use screencapture to take a screenshot and output to stdout
            result = subprocess.run([
                'screencapture', 
                '-t', 'png',  # PNG format
                '-'           # Output to stdout
            ], capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error taking screenshot: {e}")
            return b""
    
    def analyze_screenshot(self, screenshot_bytes: bytes, context: str = "") -> Dict[str, Any]:
        """Analyze a screenshot using Computer Use Preview model."""
        if not screenshot_bytes:
            return {"error": "No screenshot data"}
        
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # Construct the prompt based on context
        if context:
            prompt = f"""I'm debugging an issue with my application: {context}

Please analyze this screenshot and help me understand:
1. What's currently displayed on screen
2. Any error messages or unusual behavior visible
3. Suggestions for debugging or next steps
4. If this looks like a frontend/backend issue based on what you see

Focus on technical details that would help with debugging."""
        else:
            prompt = """Please analyze this screenshot and describe:
1. What application/interface is currently displayed
2. Any visible errors, warnings, or unusual states
3. The current state of any forms, buttons, or interactive elements
4. Any technical details that might be relevant for debugging

Be specific about what you observe."""
        
        try:
            response = self.client.responses.create(
                model=self.model,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1920,  # Adjust based on your screen
                    "display_height": 1080,
                    "environment": "mac"
                }],
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}"
                        }
                    ]
                }],
                reasoning={
                    "summary": "detailed"
                },
                truncation="auto"
            )
            
            return {
                "success": True,
                "analysis": response.output,
                "screenshot_size": len(screenshot_bytes)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze screenshot: {e}",
                "screenshot_size": len(screenshot_bytes)
            }
    
    def monitor_mode(self, interval: int = 10):
        """Continuous monitoring mode - takes screenshots at intervals."""
        print(f"Starting monitoring mode (screenshot every {interval} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n{'='*50}")
                print(f"Taking screenshot at {time.strftime('%H:%M:%S')}")
                
                screenshot = self.take_screenshot_macos()
                if screenshot:
                    result = self.analyze_screenshot(screenshot, "monitoring application state")
                    
                    if result.get("success"):
                        print("Analysis:")
                        for item in result["analysis"]:
                            if item.get("type") == "text":
                                print(item.get("text", ""))
                    else:
                        print(f"Error: {result.get('error')}")
                else:
                    print("Failed to take screenshot")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    def debug_with_context(self, context: str):
        """Take a screenshot and analyze with specific debugging context."""
        print(f"Taking screenshot for debugging: {context}")
        
        screenshot = self.take_screenshot_macos()
        if not screenshot:
            print("Failed to take screenshot")
            return
        
        result = self.analyze_screenshot(screenshot, context)
        
        if result.get("success"):
            print("\n" + "="*60)
            print("DEBUGGING ANALYSIS")
            print("="*60)
            
            for item in result["analysis"]:
                if item.get("type") == "text":
                    print(item.get("text", ""))
                elif item.get("type") == "reasoning":
                    print("\nReasoning:")
                    for summary_item in item.get("summary", []):
                        if summary_item.get("type") == "summary_text":
                            print(f"  - {summary_item.get('text')}")
        else:
            print(f"Error analyzing screenshot: {result.get('error')}")

def main():
    parser = argparse.ArgumentParser(description="Debug Vision Tool using Computer Use")
    parser.add_argument("--screenshot", action="store_true", 
                       help="Take a screenshot and analyze current state")
    parser.add_argument("--help-debug", type=str, metavar="CONTEXT",
                       help="Debug with specific context (e.g., 'agent not responding to queries')")
    parser.add_argument("--monitor", action="store_true",
                       help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=10,
                       help="Screenshot interval for monitoring mode (seconds)")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    tool = DebugVisionTool()
    
    if args.help_debug:
        tool.debug_with_context(args.help_debug)
    elif args.monitor:
        tool.monitor_mode(args.interval)
    elif args.screenshot:
        tool.debug_with_context("general application state analysis")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
