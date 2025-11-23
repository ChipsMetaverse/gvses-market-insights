#!/usr/bin/env python3
"""Query TwelveLabs video for trendline tutorial analysis"""
import os
from twelvelabs import TwelveLabs

# Initialize client with the new key
client = TwelveLabs(api_key="tlk_3HH13BP0HWYGZT216Y1HB0NEY3C4")

# Query the video
video_id = "691d2d153f41e7412f73b978"

try:
    print(f"Generating analysis for video {video_id}...")
    # Use the correct v1.1.0 API: client.analyze()
    result = client.analyze(
        video_id=video_id,
        prompt="Provide a comprehensive summary of this TradingView Lightweight Charts trendline tutorial. Include all code examples, implementation steps, key concepts, and technical details for implementing trendline drawing functionality.",
        temperature=0.2
    )

    print("\n" + "="*80)
    print("TRENDLINE TUTORIAL ANALYSIS")
    print("="*80 + "\n")
    print(f"Result ID: {result.id}")
    print(f"\n{result.data}")

    if result.usage is not None:
        print(f"\nOutput tokens: {result.usage.output_tokens}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
