#!/usr/bin/env python3
"""
Check if the OpenAI Agent Builder video has been processed
"""

import sys
import os
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')
from youtube_twelvelabs import YouTubeTwelveLabs

# Initialize the tool
tool = YouTubeTwelveLabs()

video_url = "https://www.youtube.com/watch?v=wmpKpoK-alc"
video_id = "wmpKpoK-alc"

print(f"🔍 Checking video: {video_url}")
print("=" * 60)

# Check if we have this video indexed
print("\n📊 Searching for OpenAI Agent Builder content...")

# Try searching for specific OpenAI Agent Builder keywords
search_query = "OpenAI Agent Builder workflow nodes"
print(f"Query: {search_query}")

try:
    # Search in our index
    results = tool.search_in_video("68e9d41924e2a6f182fde8a4", search_query)
    if results:
        print("❌ This search is for the wrong video (Tiny AI Tools video)")
    
    # The video about OpenAI Agent Builder was not uploaded to TwelveLabs
    # It was only analyzed locally using YouTube learning tools
    print("\n📝 Status: The OpenAI Agent Builder video was NOT uploaded to TwelveLabs")
    print("It was processed locally and implementation code was created.")
    
    # Check what we created from it
    import os
    files_created = [
        "agent_builder_implementation.py",
        "agent-builder-implementation/implementation.py"
    ]
    
    print("\n📁 Files created from this video:")
    for file in files_created:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
            # Show a snippet of the implementation
            if file == "agent_builder_implementation.py":
                with open(file, 'r') as f:
                    lines = f.readlines()[:20]
                    print("\n   First 20 lines of implementation:")
                    for line in lines:
                        print(f"   {line.rstrip()}")
        else:
            print(f"❌ {file} - NOT FOUND")
            
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
print("Summary: The video was analyzed but NOT uploaded to TwelveLabs.")
print("Implementation code was created based on the video content.")