#!/usr/bin/env python3
"""
Test script for the Deep Research Agent System
Demonstrates how to use the deep research tool for comprehensive analysis
"""

import asyncio
import json
from datetime import datetime
from deep_research_agent import (
    deep_research,
    DeepResearchOrchestrator,
    ResearchQuery,
    ResearchPhase
)


async def example_market_research():
    """Example: Market research on AI in healthcare"""
    print("=" * 80)
    print("EXAMPLE 1: Market Research - AI in Healthcare")
    print("=" * 80)
    
    query = """
    Analyze the economic impact of AI on global healthcare systems.
    Focus on:
    - Cost savings and efficiency gains
    - Investment trends and market size
    - Key players and their market share
    - Regulatory landscape
    - Future projections (5-10 years)
    """
    
    report = await deep_research(
        query=query,
        skip_clarification=False,
        data_sources=["web", "news", "academic"],
        analysis_depth="comprehensive",
        max_sources=30,
        timeout_seconds=60  # Quick demo
    )
    
    print(f"\n📊 Research Complete!")
    print(f"Sources Analyzed: {report.total_sources_analyzed}")
    print(f"Confidence Score: {report.confidence_score:.1%}")
    print(f"Duration: {report.research_duration_seconds:.1f}s")
    
    print("\n📋 Executive Summary:")
    print(report.executive_summary)
    
    print("\n🔍 Key Findings:")
    for i, finding in enumerate(report.findings[:3], 1):
        print(f"\n{i}. {finding.section_title}")
        print(f"   Confidence: {finding.confidence_level:.1%}")
        for insight in finding.key_insights[:2]:
            print(f"   • {insight}")
    
    return report


async def example_technical_research():
    """Example: Technical research on a programming topic"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Technical Research - React vs Vue.js")
    print("=" * 80)
    
    query = """
    Compare React and Vue.js for enterprise web applications.
    Analyze:
    - Performance benchmarks
    - Developer productivity
    - Ecosystem and tooling
    - Community support
    - Enterprise adoption rates
    - Best use cases for each
    """
    
    orchestrator = DeepResearchOrchestrator()
    
    # Create custom research query with specific constraints
    research_query = ResearchQuery(
        original_query=query,
        data_sources=["web", "github", "stackoverflow"],
        max_sources=25,
        analysis_depth="comprehensive",
        constraints={
            "focus_year": 2024,
            "include_code_examples": True,
            "prioritize_benchmarks": True
        }
    )
    
    report = await orchestrator.conduct_research(
        query=research_query.original_query,
        skip_clarification=True,  # Query is already detailed
        data_sources=research_query.data_sources,
        max_sources=research_query.max_sources,
        analysis_depth=research_query.analysis_depth
    )
    
    print(f"\n💻 Technical Analysis Complete!")
    print(f"Analysis Depth: {research_query.analysis_depth}")
    print(f"Primary Sources: {', '.join(research_query.data_sources)}")
    
    print("\n🎯 Recommendations:")
    for rec in report.recommendations[:3]:
        print(f"• {rec}")
    
    print("\n⚠️ Limitations:")
    for limitation in report.limitations[:2]:
        print(f"• {limitation}")
    
    return report


async def example_competitive_analysis():
    """Example: Competitive analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Competitive Analysis - Cloud Providers")
    print("=" * 80)
    
    query = """
    Conduct competitive analysis of AWS, Azure, and Google Cloud.
    Compare:
    - Market share and growth trends
    - Service offerings and unique features
    - Pricing models and cost comparison
    - Geographic presence
    - Customer satisfaction scores
    - Innovation and R&D investment
    """
    
    # Quick research with limited scope for demo
    report = await deep_research(
        query=query,
        skip_clarification=True,
        data_sources=["web", "financial_reports"],
        analysis_depth="standard",  # Faster than comprehensive
        max_sources=20,
        timeout_seconds=30
    )
    
    print(f"\n📈 Competitive Analysis Complete!")
    
    # Display in tabular format
    print("\n📊 Comparative Matrix:")
    print("-" * 60)
    
    for finding in report.findings:
        if finding.data_points:
            print(f"\n{finding.section_title}:")
            for key, value in finding.data_points.items():
                print(f"  {key}: {value}")
    
    return report


async def example_trend_analysis():
    """Example: Trend analysis and forecasting"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Trend Analysis - Remote Work Impact")
    print("=" * 80)
    
    query = """
    Analyze the long-term impact of remote work on urban real estate.
    Include:
    - Office space demand trends
    - Residential real estate shifts
    - Transportation infrastructure changes
    - Economic impact on city centers
    - Future predictions with data support
    """
    
    report = await deep_research(
        query=query,
        skip_clarification=False,
        data_sources=["web", "news", "real_estate_data"],
        analysis_depth="comprehensive",
        max_sources=40,
        include_citations=True
    )
    
    print(f"\n🏢 Trend Analysis Complete!")
    
    print("\n📈 Identified Trends:")
    for finding in report.findings:
        if "trend" in finding.section_title.lower():
            print(f"\n• {finding.section_title}")
            if finding.data_points.get("trend"):
                print(f"  Direction: {finding.data_points['trend']}")
            if finding.data_points.get("impact_scale"):
                print(f"  Impact: {finding.data_points['impact_scale']}")
    
    # Show citations
    print("\n📚 Key Citations:")
    for citation in report.citations[:5]:
        print(f"• {citation.get('title', 'Untitled')} - {citation.get('type', 'web')}")
    
    return report


async def example_with_real_apis():
    """Example showing how to integrate with real APIs"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Real API Integration Demo")
    print("=" * 80)
    
    # This example shows how you would integrate with real services
    api_keys = {
        "perplexity": "your-perplexity-api-key",
        "openai": "your-openai-api-key",
        "google": "your-google-api-key"
    }
    
    orchestrator = DeepResearchOrchestrator(api_keys=api_keys)
    
    query = "What are the latest breakthroughs in quantum computing?"
    
    print("\n🔧 Integration Points:")
    print("• Perplexity API for deep web research")
    print("• OpenAI API for analysis and synthesis")
    print("• Google Scholar API for academic sources")
    print("• News APIs for recent developments")
    
    print("\n💡 To enable real API calls:")
    print("1. Add API keys to environment variables")
    print("2. Implement API clients in DataGatheringAgent")
    print("3. Update AnalysisAgent to use LLM APIs")
    print("4. Enhance SynthesisAgent with GPT-4 synthesis")
    
    # For demo, use mock research
    report = await deep_research(
        query=query,
        skip_clarification=True,
        data_sources=["web"],
        analysis_depth="quick",
        max_sources=10
    )
    
    print(f"\n✅ Research Framework Ready!")
    print("The deep research system is ready for API integration.")
    
    return report


async def save_research_report(report, filename):
    """Save research report to JSON file"""
    report_dict = {
        "timestamp": datetime.now().isoformat(),
        "query": report.query.original_query,
        "executive_summary": report.executive_summary,
        "findings": [
            {
                "title": f.section_title,
                "content": f.content,
                "confidence": f.confidence_level,
                "insights": f.key_insights
            }
            for f in report.findings
        ],
        "methodology": report.methodology,
        "recommendations": report.recommendations,
        "limitations": report.limitations,
        "statistics": {
            "total_sources": report.total_sources_analyzed,
            "duration_seconds": report.research_duration_seconds,
            "confidence_score": report.confidence_score
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(report_dict, f, indent=2)
    
    print(f"\n💾 Report saved to: {filename}")


async def main():
    """Run all examples"""
    print("\n" + "🚀 " * 20)
    print("DEEP RESEARCH AGENT SYSTEM - DEMONSTRATION")
    print("🚀 " * 20)
    
    # Run examples
    reports = []
    
    # Example 1: Market Research
    report1 = await example_market_research()
    reports.append(report1)
    await asyncio.sleep(1)
    
    # Example 2: Technical Research
    report2 = await example_technical_research()
    reports.append(report2)
    await asyncio.sleep(1)
    
    # Example 3: Competitive Analysis
    report3 = await example_competitive_analysis()
    reports.append(report3)
    await asyncio.sleep(1)
    
    # Example 4: Trend Analysis
    report4 = await example_trend_analysis()
    reports.append(report4)
    
    # Example 5: API Integration Guide
    report5 = await example_with_real_apis()
    reports.append(report5)
    
    # Save a sample report
    if reports:
        await save_research_report(
            reports[0],
            "sample_research_report.json"
        )
    
    print("\n" + "=" * 80)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("\n📌 Key Capabilities Demonstrated:")
    print("✅ Multi-phase research process")
    print("✅ Parallel data gathering")
    print("✅ Comprehensive analysis")
    print("✅ Synthesis and validation")
    print("✅ Professional report generation")
    print("✅ Citation management")
    print("✅ Confidence scoring")
    print("✅ Customizable research depth")
    
    print("\n🔗 Integration Ready For:")
    print("• Perplexity API for advanced search")
    print("• OpenAI GPT-4 for analysis")
    print("• Web scraping with Playwright")
    print("• Academic database APIs")
    print("• Real-time data feeds")
    
    print("\n📘 Next Steps:")
    print("1. Add real API integrations")
    print("2. Enhance with actual LLM calls")
    print("3. Implement caching for efficiency")
    print("4. Add visualization capabilities")
    print("5. Create web interface")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())