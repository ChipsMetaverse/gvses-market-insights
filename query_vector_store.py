#!/usr/bin/env python3
"""Query TwelveLabs for Vector Store node details"""

import os
import sys
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')

from youtube_twelvelabs import YouTubeTwelveLabs

def main():
    tool = YouTubeTwelveLabs()
    video_id = "68e70261475d6f0e633dc5e8"

    prompt = """Explain in detail how to configure and use the Vector Store node in Agent Builder. Include:

1) How to add Vector Store to the canvas
2) What settings/properties the Vector Store node has
3) How to upload documents/data to the Vector Store
4) How to connect Vector Store to other nodes (especially Agent nodes)
5) What are the use cases shown in the video
6) Best practices for using Vector Store
7) Any specific examples of Vector Store being configured or used
8) What file types can be stored
9) How agents retrieve information from Vector Store
10) Any limitations or requirements mentioned"""

    print("Querying TwelveLabs about Vector Store node...")
    result = tool.analyze_video(video_id, prompt)

    print("\n" + "="*80)
    print("VECTOR STORE CONFIGURATION DETAILS")
    print("="*80)
    print(result["analysis"])
    print("="*80)

if __name__ == "__main__":
    main()
