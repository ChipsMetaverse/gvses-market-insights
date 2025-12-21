#!/usr/bin/env python3
"""
Analyze chartData count from Agent Builder response snapshot.
This script parses the JSON we captured and counts actual chartData entries.
"""

import json
import re

# JSON response from G'sves agent (extracted from Playwright snapshot)
# This is the complete visible portion from the test
json_response_snippet = """{"company":"Apple, Inc.","symbol":"AAPL","timestamp":"Updated Nov 22, 2025 3:15 PM ET","price":{"current":"$271.49","changeLabel":"+5.24 (1.97%)","changeColor":"success","afterHours":{"price":"$271.35","changeLabel":"-0.14 (-0.05%)","changeColor":"destructive"}},"timeframes":["1D","5D","1M","3M","6M","1Y","YTD","MAX"],"selectedTimeframe":"1D","chartData":[{"date":"2025-07-03","open":212.14999389648438,"high":214.64999389648438,"low":211.80999755859375,"close":213.5500030517578,"volume":34955800},{"date":"2025-07-07","open":212.67999267578125,"high":216.22999572753906,"low":208.8000030517578,"close":209.9499969482422,"volume":50229000}"""

# Since we only have a snippet, let's analyze what we can see and extrapolate

# Count date entries in the snippet
date_pattern = r'"date":"2025-\d{2}-\d{2}"'
visible_dates = re.findall(date_pattern, json_response_snippet)

print("=== ChartData Analysis ===\n")
print(f"Visible chartData entries in snippet: {len(visible_dates)}")
print(f"First date: {visible_dates[0] if visible_dates else 'N/A'}")
print(f"Last visible date: {visible_dates[-1] if visible_dates else 'N/A'}")

# From the full snapshot data, we saw dates ranging from July to October
# Let's estimate based on business days
from datetime import datetime, timedelta

start_date = datetime(2025, 7, 3)  # First date we saw
end_date = datetime(2025, 10, 27)  # Last date we saw

# Calculate business days (rough estimate)
delta = end_date - start_date
total_days = delta.days
estimated_business_days = int(total_days * 5/7)  # Approximate business days

print(f"\n=== Date Range Analysis ===")
print(f"Start: {start_date.date()}")
print(f"End: {end_date.date()}")
print(f"Total calendar days: {total_days}")
print(f"Estimated business days: {estimated_business_days}")

print(f"\n=== Key Findings ===")
print(f"• Agent stated: '40 items'")
print(f"• Actual date range: ~{estimated_business_days} business days")
print(f"• Visible in snapshot: {len(visible_dates)} entries (truncated)")

if estimated_business_days > 50:
    print(f"\n⚠️  WARNING: {estimated_business_days} days exceeds target of 30-50 points!")
    print("Option 1 (MCP enum modification) may NOT be working.")
elif estimated_business_days <= 50:
    print(f"\n✅ GOOD: {estimated_business_days} days is within target range!")
    print("Option 1 appears to be working correctly.")

print(f"\n=== Metadata ===")
if '"count":11329' in json_response_snippet or 'count' in json_response_snippet.lower():
    print("• Found 'count' field in response (unclear meaning)")
else:
    print("• No 'count' metadata field visible in snippet")

print("\n=== Recommendation ===")
print("Need to extract FULL JSON response to get exact chartData.length")
print("Options:")
print("1. Access Agent Builder logs (requires re-authentication)")
print("2. Run another test and capture complete response")
print("3. Add console.log in agent to output chartData.length")
