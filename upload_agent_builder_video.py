#!/usr/bin/env python3
"""Upload the sped-up Agent Builder video to TwelveLabs"""

import sys
import os
from pathlib import Path

# Add youtube-twelvelabs to path
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')

from youtube_twelvelabs import YouTubeTwelveLabs
from rich.console import Console

console = Console()

def main():
    video_path = Path('/Users/MarcoPolo/Downloads/agent_builder_1.4x.mp4')

    # Check if video exists
    if not video_path.exists():
        console.print(f"[red]Error:[/red] Video not found at {video_path}")
        console.print("[yellow]Waiting for ffmpeg to complete...[/yellow]")
        return 1

    # Get file size
    size_mb = video_path.stat().st_size / (1024 * 1024)
    console.print(f"[cyan]Video file:[/cyan] {video_path.name}")
    console.print(f"[cyan]Size:[/cyan] {size_mb:.2f} MB")

    # Initialize tool
    console.print("\n[cyan]Initializing TwelveLabs...[/cyan]")
    tool = YouTubeTwelveLabs()

    # Upload video
    console.print("\n[cyan]Uploading video to TwelveLabs...[/cyan]")
    console.print("[yellow]This may take several minutes...[/yellow]\n")

    try:
        video_id = tool.upload_video(video_path, wait=True)

        console.print(f"\n[green]✓ Upload successful![/green]")
        console.print(f"[green]Video ID:[/green] {video_id}")
        console.print(f"\n[cyan]You can now analyze this video using:[/cyan]")
        console.print(f"python3 query_vector_store.py  # Update video_id to: {video_id}")

        return 0

    except Exception as e:
        console.print(f"\n[red]Upload failed:[/red] {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
