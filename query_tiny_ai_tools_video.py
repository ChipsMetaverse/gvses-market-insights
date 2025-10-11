#!/usr/bin/env python3
"""
Query the indexed video for implementation walkthrough of tiny AI tools
"""

import sys
import os
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')
from youtube_twelvelabs import YouTubeTwelveLabs

# Initialize the tool
tool = YouTubeTwelveLabs()

# Video ID from the upload
video_id = "68e9d41924e2a6f182fde8a4"

print("🔍 Analyzing video: He Makes $3M/Year From Tiny AI Tools")
print("=" * 60)

# Query 1: Get the overall strategy and tools mentioned
print("\n📋 PART 1: Overall Strategy & Tools Overview")
print("-" * 40)
strategy_query = """
What are all the tiny AI tools mentioned in this video that generate revenue?
List each tool, its purpose, and how it makes money.
Include specific examples and the creator's success stories.
"""
results = tool.search_in_video(video_id, strategy_query)
if results:
    for i, result in enumerate(results[:3], 1):
        print(f"\nResult {i}:")
        if isinstance(result, dict):
            start = result.get('start', 0)
            end = result.get('end', 0)
            confidence = result.get('confidence', 0)
            print(f"[{start:.1f}s - {end:.1f}s]", end="")
            if confidence:
                try:
                    print(f" Confidence: {float(confidence):.2f}")
                except:
                    print(f" Confidence: {confidence}")
            if result.get('text'):
                print(f"Transcript: {result['text'][:500]}...")  # Limit text length

# Query 2: Implementation details
print("\n\n🛠️ PART 2: Implementation Walkthrough")
print("-" * 40)
implementation_query = """
Show me the exact implementation steps, code examples, or technical details 
for building these tiny AI tools. Include any specific frameworks, APIs, 
or technologies mentioned.
"""
results = tool.search_in_video(video_id, implementation_query)
if results:
    for i, result in enumerate(results[:3], 1):
        print(f"\nResult {i}:")
        if isinstance(result, dict):
            start = result.get('start', 0)
            end = result.get('end', 0)
            confidence = result.get('confidence', 0)
            print(f"[{start:.1f}s - {end:.1f}s]", end="")
            if confidence:
                try:
                    print(f" Confidence: {float(confidence):.2f}")
                except:
                    print(f" Confidence: {confidence}")
            if result.get('text'):
                print(f"Transcript: {result['text'][:500]}...")  # Limit text length

# Query 3: Business model and monetization
print("\n\n💰 PART 3: Business Model & Monetization")
print("-" * 40)
business_query = """
How does the creator monetize these tiny AI tools? 
What pricing strategies, platforms, or distribution methods are used?
Include revenue numbers and growth strategies mentioned.
"""
results = tool.search_in_video(video_id, business_query)
if results:
    for i, result in enumerate(results[:3], 1):
        print(f"\nResult {i}:")
        if isinstance(result, dict):
            start = result.get('start', 0)
            end = result.get('end', 0)
            confidence = result.get('confidence', 0)
            print(f"[{start:.1f}s - {end:.1f}s]", end="")
            if confidence:
                try:
                    print(f" Confidence: {float(confidence):.2f}")
                except:
                    print(f" Confidence: {confidence}")
            if result.get('text'):
                print(f"Transcript: {result['text'][:500]}...")  # Limit text length

# Query 4: Specific tool demonstrations
print("\n\n🎯 PART 4: Specific Tool Demonstrations")
print("-" * 40)
demo_query = """
Show any demonstrations, walkthroughs, or examples of the actual tools in action.
Include UI/UX details, features, and how users interact with the tools.
"""
results = tool.search_in_video(video_id, demo_query)
if results:
    for i, result in enumerate(results[:3], 1):
        print(f"\nResult {i}:")
        if isinstance(result, dict):
            start = result.get('start', 0)
            end = result.get('end', 0)
            confidence = result.get('confidence', 0)
            print(f"[{start:.1f}s - {end:.1f}s]", end="")
            if confidence:
                try:
                    print(f" Confidence: {float(confidence):.2f}")
                except:
                    print(f" Confidence: {confidence}")
            if result.get('text'):
                print(f"Transcript: {result['text'][:500]}...")  # Limit text length

# Query 5: Key success factors and tips
print("\n\n✨ PART 5: Key Success Factors & Tips")
print("-" * 40)
tips_query = """
What are the key success factors, tips, or advice given for building 
successful tiny AI tools? Include marketing strategies, tool selection criteria,
and common mistakes to avoid.
"""
results = tool.search_in_video(video_id, tips_query)
if results:
    for i, result in enumerate(results[:3], 1):
        print(f"\nResult {i}:")
        if isinstance(result, dict):
            start = result.get('start', 0)
            end = result.get('end', 0)
            confidence = result.get('confidence', 0)
            print(f"[{start:.1f}s - {end:.1f}s]", end="")
            if confidence:
                try:
                    print(f" Confidence: {float(confidence):.2f}")
                except:
                    print(f" Confidence: {confidence}")
            if result.get('text'):
                print(f"Transcript: {result['text'][:500]}...")  # Limit text length

print("\n" + "=" * 60)
print("📊 Analysis complete! Ready to implement tiny AI tools.")