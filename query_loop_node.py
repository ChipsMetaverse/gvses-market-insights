#!/usr/bin/env python3
"""Query TwelveLabs for Loop Node details"""

import os
import sys
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')

from youtube_twelvelabs import YouTubeTwelveLabs

def main():
    tool = YouTubeTwelveLabs()
    video_id = "68e70261475d6f0e633dc5e8"

    prompt = """Explain in detail how to configure and use the Loop node in Agent Builder. Include:

1) How to add Loop node to the canvas
2) What settings/properties the Loop node has
3) How to configure loop iterations (for, while, foreach, etc.)
4) How to pass data into the loop (arrays, lists, etc.)
5) How to connect Loop node to other nodes
6) What happens inside the loop body
7) How to exit the loop or set exit conditions
8) Use cases shown in the video for Loop node
9) Best practices for using loops in workflows
10) Any specific examples of Loop being configured or used
11) How to handle loop output/results
12) Any limitations or performance considerations mentioned"""

    print("Querying TwelveLabs about Loop node...")
    result = tool.analyze_video(video_id, prompt)

    print("\n" + "="*80)
    print("LOOP NODE CONFIGURATION DETAILS")
    print("="*80)
    print(result["analysis"])
    print("="*80)

if __name__ == "__main__":
    main()
