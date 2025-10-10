#!/usr/bin/env python3
"""Comprehensive analysis of the Agent Builder 1-hour tutorial video"""

import sys
import os
from pathlib import Path

# Add youtube-twelvelabs to path
sys.path.append('/Users/MarcoPolo/workspace/PROJECTS/tools/youtube-twelvelabs')

from youtube_twelvelabs import YouTubeTwelveLabs
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def main():
    tool = YouTubeTwelveLabs()
    video_id = "68e7205af2596962dd422eb2"  # 1.4x sped-up version

    # Comprehensive analysis prompts
    analysis_topics = [
        {
            "name": "Complete Node Types Inventory",
            "prompt": """List EVERY node type shown in the Agent Builder interface throughout the entire video. For each node type, provide:
1. Exact node name as shown in the UI
2. What category it's in (if shown)
3. When it's first introduced (approximate timestamp)
4. What it's used for
5. Any special properties or settings mentioned

Include ALL nodes, even ones briefly shown or mentioned."""
        },
        {
            "name": "Vector Store Deep Dive",
            "prompt": """Provide exhaustive details about the Vector Store node:
1. Complete upload workflow (every step shown)
2. ALL file types explicitly mentioned or shown being uploaded
3. Drag-and-drop vs button upload - which methods are demonstrated?
4. Vectorization process - what happens, how long it takes, progress indicators
5. How to connect to agents - exact connection patterns shown
6. Index and Embeddings settings - what options are available?
7. Performance considerations mentioned
8. Best practices for document organization
9. Any limitations or warnings mentioned
10. Example use cases demonstrated in the video"""
        },
        {
            "name": "Loop Node Complete Guide",
            "prompt": """Extract ALL information about the Loop node:
1. When is it first introduced?
2. What types of loops are available? (ForEach, While, etc.)
3. Complete configuration options shown
4. How to set up iteration variables
5. How to connect Loop nodes in workflows
6. Example use cases demonstrated
7. Input/output handling
8. Exit conditions and break logic
9. Best practices mentioned
10. Any advanced features or tricks shown"""
        },
        {
            "name": "MCP Integration Details",
            "prompt": """Document everything about MCP (Model Context Protocol) integration:
1. How to add MCP servers to Agent Builder
2. Configuration steps shown
3. Example MCP servers used in demos
4. How to call MCP tools from agents
5. Authentication/API key setup
6. Testing MCP connections
7. Error handling for MCP failures
8. Best practices for MCP integration
9. Limitations mentioned
10. Any advanced MCP features shown"""
        },
        {
            "name": "Agent Node Configuration",
            "prompt": """Detailed breakdown of Agent node configuration:
1. All available settings/properties for Agent nodes
2. How to write effective agent instructions
3. Model selection options shown
4. Temperature and parameter settings
5. How to connect agents to other nodes (inputs/outputs)
6. Multi-agent workflows demonstrated
7. Agent communication patterns
8. Context passing between agents
9. Best practices for agent instruction writing
10. Common mistakes or warnings mentioned"""
        },
        {
            "name": "Workflow Patterns and Architecture",
            "prompt": """Identify all workflow patterns demonstrated:
1. Linear workflows (simple chains)
2. Branching workflows (Classification → multiple paths)
3. Multi-agent collaboration patterns
4. Loop-based patterns
5. Error handling patterns
6. Parallel processing patterns
7. How to structure complex workflows
8. Common workflow mistakes shown/mentioned
9. Best practices for workflow design
10. Example applications and their architectures"""
        },
        {
            "name": "Testing and Debugging",
            "prompt": """How to test and debug Agent Builder workflows:
1. Testing individual nodes
2. Testing complete workflows
3. Debug tools available in the interface
4. How to view node outputs
5. Error messages and how to interpret them
6. Common debugging scenarios shown
7. Best practices for testing
8. How to validate agent responses
9. Performance monitoring
10. Iteration and improvement strategies"""
        },
        {
            "name": "Production Deployment",
            "prompt": """Details about deploying Agent Builder workflows:
1. How to publish/deploy workflows
2. API access to deployed agents
3. Versioning and updates
4. Monitoring production agents
5. Scaling considerations mentioned
6. Cost optimization tips
7. Security best practices
8. Integration with external systems
9. Webhook or API endpoint setup
10. Any deployment examples shown"""
        },
        {
            "name": "Advanced Features and Tips",
            "prompt": """Extract all advanced features, tips, and tricks:
1. Hidden or advanced features demonstrated
2. Keyboard shortcuts shown
3. UI tips and workflow efficiency
4. Advanced node configurations
5. Optimization techniques
6. Common pitfalls to avoid
7. Pro tips mentioned by instructor
8. Lesser-known features
9. Future roadmap hints
10. Any "insider knowledge" shared"""
        },
        {
            "name": "Complete Demo Applications",
            "prompt": """Document EVERY demo application built in the video:
1. List all demos with names
2. For each demo, provide:
   - Purpose/use case
   - Complete node structure
   - Key configurations
   - Special features demonstrated
   - Lessons learned
   - How it showcases specific capabilities
3. Timeline of when each demo is shown
4. Complexity progression
5. Which demos are most relevant for learning"""
        }
    ]

    console.print(f"[cyan]Starting comprehensive analysis of video {video_id}[/cyan]")
    console.print(f"[yellow]Total analysis topics: {len(analysis_topics)}[/yellow]\n")

    results = {}

    for i, topic in enumerate(analysis_topics, 1):
        console.print(f"[bold cyan]Topic {i}/{len(analysis_topics)}: {topic['name']}[/bold cyan]")
        console.print(f"[dim]{topic['prompt'][:100]}...[/dim]\n")

        try:
            result = tool.analyze_video(video_id, topic['prompt'])
            results[topic['name']] = result['analysis']

            console.print(f"[green]✓ Completed: {topic['name']}[/green]")
            console.print(f"[dim]Response length: {len(result['analysis'])} characters[/dim]\n")

        except Exception as e:
            console.print(f"[red]✗ Failed: {topic['name']}[/red]")
            console.print(f"[red]Error: {str(e)}[/red]\n")
            results[topic['name']] = f"ERROR: {str(e)}"

    # Save complete analysis
    output_file = Path("AGENT_BUILDER_COMPREHENSIVE_ANALYSIS.md")

    with open(output_file, 'w') as f:
        f.write("# Agent Builder Comprehensive Video Analysis\n\n")
        f.write(f"**Video ID**: {video_id} (1.4x speed version)\n")
        f.write(f"**Analysis Date**: {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Total Topics Analyzed**: {len(analysis_topics)}\n\n")
        f.write("---\n\n")

        for topic in analysis_topics:
            name = topic['name']
            f.write(f"## {name}\n\n")

            if name in results:
                f.write(results[name])
            else:
                f.write("*No data available*")

            f.write("\n\n---\n\n")

    console.print(f"\n[green]✓ Analysis complete![/green]")
    console.print(f"[cyan]Saved to:[/cyan] {output_file}")

    # Display summary
    console.print(f"\n[bold]Analysis Summary:[/bold]")
    for topic in analysis_topics:
        name = topic['name']
        if name in results and not results[name].startswith("ERROR"):
            length = len(results[name])
            console.print(f"  [green]✓[/green] {name}: {length:,} chars")
        else:
            console.print(f"  [red]✗[/red] {name}: Failed")

if __name__ == "__main__":
    main()
