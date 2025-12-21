#!/usr/bin/env python3
"""
Simple test to verify Chart Analysis Panel is working with MCP data parsing fixes.
Uses direct MCP Playwright function calls.
"""

import json
from datetime import datetime

# First navigate to the frontend
print("🚀 Testing Chart Analysis Panel MCP Data Parsing Fixes")
print("=" * 60)

# Navigate to the frontend URL
frontend_url = "http://localhost:5175"
print(f"📱 Navigating to: {frontend_url}")