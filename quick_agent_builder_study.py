#!/usr/bin/env python3
"""Quick focused study of Agent Builder video - most critical topics"""

import sys
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')

from youtube_twelvelabs import YouTubeTwelveLabs
from pathlib import Path

def main():
    tool = YouTubeTwelveLabs()
    video_id = "68e7205af2596962dd422eb2"

    # Focus on 3 most critical topics for G'sves migration
    critical_topics = [
        {
            "name": "All_Node_Types",
            "prompt": "List every single node type visible in the Agent Builder interface. Include node names, categories, and brief descriptions."
        },
        {
            "name": "Vector_Store_Complete",
            "prompt": "Complete Vector Store documentation: upload methods (drag-drop vs button), file types supported, Index/Embeddings properties, connection patterns, performance warnings about context size."
        },
        {
            "name": "Loop_Node_Details",
            "prompt": "Loop node: types available (ForEach, While, etc), configuration options, how to iterate arrays, exit conditions, example use cases shown."
        }
    ]

    output = Path("AGENT_BUILDER_CRITICAL_FINDINGS.md")

    with open(output, 'w') as f:
        f.write("# Agent Builder Critical Findings\n\n")
        f.write(f"Video: {video_id}\n\n---\n\n")

        for topic in critical_topics:
            print(f"\nAnalyzing: {topic['name']}...")

            try:
                result = tool.analyze_video(video_id, topic['prompt'])

                f.write(f"## {topic['name']}\n\n")
                f.write(result['analysis'])
                f.write("\n\n---\n\n")
                f.flush()  # Save immediately

                print(f"✓ Saved {topic['name']}")

            except Exception as e:
                print(f"✗ Error: {str(e)}")
                f.write(f"## {topic['name']}\n\nERROR: {str(e)}\n\n---\n\n")
                f.flush()

    print(f"\n✓ Complete! Saved to: {output}")

if __name__ == "__main__":
    main()
