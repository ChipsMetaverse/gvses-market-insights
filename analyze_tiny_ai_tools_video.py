#!/usr/bin/env python3
"""
Analyze and summarize the tiny AI tools video
"""

import sys
import os
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')
from youtube_twelvelabs import YouTubeTwelveLabs
import json

# Initialize the tool
tool = YouTubeTwelveLabs()

# Video ID from the upload
video_id = "68e9d41924e2a6f182fde8a4"

print("🎬 Analyzing video: He Makes $3M/Year From Tiny AI Tools")
print("=" * 60)

try:
    # Generate a comprehensive summary
    print("\n📊 GENERATING VIDEO SUMMARY...")
    print("-" * 40)
    summary = tool.generate_summary(video_id)
    
    if summary:
        print("\n📝 VIDEO SUMMARY:")
        print(summary)
    else:
        print("No summary generated")
    
    # Try analyzing the video
    print("\n\n🔍 ANALYZING VIDEO CONTENT...")
    print("-" * 40)
    analysis = tool.analyze_video(video_id)
    
    if analysis:
        print("\n📈 VIDEO ANALYSIS:")
        if isinstance(analysis, dict):
            print(json.dumps(analysis, indent=2))
        else:
            print(analysis)
    else:
        print("No analysis generated")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    
    # Try simple search as fallback
    print("\n\n🔄 FALLBACK: Simple keyword search...")
    print("-" * 40)
    
    keywords = ["AI tools", "money", "revenue", "build", "create", "app", "software", "tool"]
    for keyword in keywords:
        print(f"\n🔎 Searching for: '{keyword}'")
        try:
            results = tool.search_in_video(video_id, keyword)
            if results and len(results) > 0:
                result = results[0]
                if isinstance(result, dict):
                    print(f"Found at {result.get('start', 0):.1f}s - {result.get('end', 0):.1f}s")
                    if result.get('text'):
                        print(f"Context: {result['text'][:200]}...")
                else:
                    print(f"Result: {str(result)[:200]}...")
        except Exception as search_error:
            print(f"Search failed: {search_error}")

print("\n" + "=" * 60)
print("✅ Analysis complete!")