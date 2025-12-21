#!/usr/bin/env python3
"""
Test script to debug agent builder and widget issues.
"""

import asyncio
from datetime import datetime

async def debug_agent_widget_issue():
    """Debug agent builder and widget issues."""
    
    print("🚀 Starting Agent/Widget Debugging")
    print("=" * 60)
    
    # Navigate to the frontend
    frontend_url = "http://localhost:5174" # Assuming this is the correct port
    print(f"📱 Navigating to frontend: {frontend_url}")
    
    try:
        # Use MCP Playwright tools
        from claude_code import mcp__playwright__browser_navigate, mcp__playwright__browser_wait_for, mcp__playwright__browser_take_screenshot
        
        await mcp__playwright__browser_navigate(url=frontend_url)
        print("✅ Successfully navigated to frontend")
        
        # Wait for the page to load
        await mcp__playwright__browser_wait_for(time=5)
        
        # Take a screenshot
        screenshot_filename = f"agent_widget_debug_{int(datetime.now().timestamp())}.png"
        await mcp__playwright__browser_take_screenshot(filename=screenshot_filename)
        print(f"📸 Screenshot saved: {screenshot_filename}")
        
        # More debugging steps will be added here
        
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        error_screenshot = f"agent_widget_debug_error_{int(datetime.now().timestamp())}.png"
        try:
            await mcp__playwright__browser_take_screenshot(filename=error_screenshot)
            print(f"📸 Error screenshot saved: {error_screenshot}")
        except:
            pass
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🧪 Debugging Agent Builder and Widget Issues")
    print("=" * 60)
    
    asyncio.run(debug_agent_widget_issue())
