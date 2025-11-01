"""
Deep Research Agent System
Inspired by OpenAI's o3-deep-research and o4-mini-deep-research models
This system orchestrates multiple specialized agents for comprehensive research
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchPhase(Enum):
    """Phases of the research process"""
    CLARIFICATION = "clarification"
    PROMPT_REWRITING = "prompt_rewriting"
    RESEARCH_PLANNING = "research_planning"
    DATA_GATHERING = "data_gathering"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    REPORT_GENERATION = "report_generation"


@dataclass
class ResearchQuery:
    """Structure for research queries"""
    original_query: str
    clarified_query: Optional[str] = None
    rewritten_prompt: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    data_sources: List[str] = field(default_factory=list)
    max_sources: int = 100
    timeout_seconds: int = 3600
    include_citations: bool = True
    analysis_depth: str = "comprehensive"  # quick, standard, comprehensive, exhaustive


@dataclass
class ResearchSource:
    """Structure for research sources"""
    url: Optional[str] = None
    title: str = ""
    content: str = ""
    source_type: str = "web"  # web, file, api, database
    credibility_score: float = 0.0
    relevance_score: float = 0.0
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchFindings:
    """Structure for research findings"""
    section_title: str
    content: str
    sources: List[ResearchSource]
    confidence_level: float
    key_insights: List[str]
    data_points: Dict[str, Any]
    
    
@dataclass
class ResearchReport:
    """Complete research report structure"""
    query: ResearchQuery
    executive_summary: str
    findings: List[ResearchFindings]
    methodology: str
    limitations: List[str]
    recommendations: List[str]
    total_sources_analyzed: int
    research_duration_seconds: float
    confidence_score: float
    citations: List[Dict[str, Any]]
    raw_data: Optional[Dict[str, Any]] = None


class DeepResearchOrchestrator:
    """Main orchestrator for deep research tasks"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.research_agents = {
            "clarifier": ClarificationAgent(),
            "rewriter": PromptRewritingAgent(),
            "planner": ResearchPlanningAgent(),
            "gatherer": DataGatheringAgent(),
            "analyzer": AnalysisAgent(),
            "synthesizer": SynthesisAgent(),
            "validator": ValidationAgent(),
            "reporter": ReportGenerationAgent()
        }
        
    async def conduct_research(
        self,
        query: str,
        skip_clarification: bool = False,
        data_sources: Optional[List[str]] = None,
        **kwargs
    ) -> ResearchReport:
        """
        Main entry point for conducting deep research
        
        Args:
            query: The research question or topic
            skip_clarification: Skip the clarification step if query is detailed
            data_sources: List of data sources to use (web, files, apis, etc.)
            **kwargs: Additional parameters for research configuration
            
        Returns:
            ResearchReport with comprehensive findings
        """
        start_time = datetime.now()
        
        # Initialize research query
        research_query = ResearchQuery(
            original_query=query,
            data_sources=data_sources or ["web", "perplexity", "context7"],
            **kwargs
        )
        
        try:
            # Phase 1: Clarification (optional)
            if not skip_clarification:
                research_query = await self._clarify_query(research_query)
                
            # Phase 2: Prompt Rewriting
            research_query = await self._rewrite_prompt(research_query)
            
            # Phase 3: Research Planning
            research_plan = await self._plan_research(research_query)
            
            # Phase 4: Data Gathering (parallel)
            raw_data = await self._gather_data(research_query, research_plan)
            
            # Phase 5: Analysis
            analyzed_data = await self._analyze_data(raw_data, research_query)
            
            # Phase 6: Synthesis
            synthesized_findings = await self._synthesize_findings(analyzed_data, research_query)
            
            # Phase 7: Validation
            validated_findings = await self._validate_findings(synthesized_findings, raw_data)
            
            # Phase 8: Report Generation
            report = await self._generate_report(
                research_query,
                validated_findings,
                raw_data,
                (datetime.now() - start_time).total_seconds()
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            raise
            
    async def _clarify_query(self, query: ResearchQuery) -> ResearchQuery:
        """Clarify and expand the research query"""
        clarified = await self.research_agents["clarifier"].clarify(query)
        query.clarified_query = clarified
        return query
        
    async def _rewrite_prompt(self, query: ResearchQuery) -> ResearchQuery:
        """Rewrite the prompt for better research results"""
        rewritten = await self.research_agents["rewriter"].rewrite(query)
        query.rewritten_prompt = rewritten
        return query
        
    async def _plan_research(self, query: ResearchQuery) -> Dict[str, Any]:
        """Create a research plan"""
        return await self.research_agents["planner"].plan(query)
        
    async def _gather_data(self, query: ResearchQuery, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Gather data from multiple sources in parallel"""
        return await self.research_agents["gatherer"].gather(query, plan)
        
    async def _analyze_data(self, data: Dict[str, Any], query: ResearchQuery) -> Dict[str, Any]:
        """Analyze gathered data"""
        return await self.research_agents["analyzer"].analyze(data, query)
        
    async def _synthesize_findings(self, data: Dict[str, Any], query: ResearchQuery) -> List[ResearchFindings]:
        """Synthesize findings from analyzed data"""
        return await self.research_agents["synthesizer"].synthesize(data, query)
        
    async def _validate_findings(self, findings: List[ResearchFindings], raw_data: Dict[str, Any]) -> List[ResearchFindings]:
        """Validate findings against raw data"""
        return await self.research_agents["validator"].validate(findings, raw_data)
        
    async def _generate_report(
        self,
        query: ResearchQuery,
        findings: List[ResearchFindings],
        raw_data: Dict[str, Any],
        duration: float
    ) -> ResearchReport:
        """Generate final research report"""
        return await self.research_agents["reporter"].generate(query, findings, raw_data, duration)


class ClarificationAgent:
    """Agent for clarifying research queries"""
    
    async def clarify(self, query: ResearchQuery) -> str:
        """
        Clarify the research query by identifying:
        - Specific aspects to focus on
        - Time constraints
        - Geographic constraints
        - Data preferences
        - Output format requirements
        """
        clarification_prompt = f"""
        Clarify this research query: '{query.original_query}'
        
        Expand it to include:
        1. Specific aspects that should be researched
        2. Time period to focus on (if applicable)
        3. Geographic scope (if applicable)
        4. Types of sources preferred
        5. Key metrics or data points needed
        6. Any constraints or limitations
        
        Return a clear, detailed research question.
        """
        
        # In production, this would call an LLM API
        # For now, we'll return an enhanced version
        clarified = f"""
        Research Task: {query.original_query}
        
        Scope:
        - Focus on recent developments (last 2 years)
        - Include quantitative data and statistics
        - Prioritize peer-reviewed and authoritative sources
        - Cover global perspective with regional variations
        - Include expert opinions and case studies
        """
        
        return clarified


class PromptRewritingAgent:
    """Agent for rewriting prompts for optimal research"""
    
    async def rewrite(self, query: ResearchQuery) -> str:
        """
        Rewrite the prompt to be more specific and actionable
        """
        base_query = query.clarified_query or query.original_query
        
        rewritten = f"""
        Comprehensive Research Request: {base_query}
        
        Requirements:
        - Provide specific figures, trends, statistics, and measurable outcomes
        - Include inline citations for all claims
        - Structure findings in clear sections
        - Highlight key insights and patterns
        - Address potential counterarguments
        - Include methodology and limitations
        - Provide actionable recommendations
        
        Data Sources: {', '.join(query.data_sources)}
        Analysis Depth: {query.analysis_depth}
        Max Sources: {query.max_sources}
        """
        
        return rewritten


class ResearchPlanningAgent:
    """Agent for planning research approach"""
    
    async def plan(self, query: ResearchQuery) -> Dict[str, Any]:
        """
        Create a detailed research plan
        """
        plan = {
            "phases": [
                {
                    "name": "Initial Survey",
                    "objectives": ["Understand landscape", "Identify key sources"],
                    "sources": ["web_search", "academic_databases"],
                    "estimated_sources": 20
                },
                {
                    "name": "Deep Dive",
                    "objectives": ["Gather detailed data", "Expert opinions"],
                    "sources": ["specialized_apis", "research_papers"],
                    "estimated_sources": 50
                },
                {
                    "name": "Comparative Analysis",
                    "objectives": ["Compare perspectives", "Identify patterns"],
                    "sources": ["cross_reference", "meta_analysis"],
                    "estimated_sources": 30
                }
            ],
            "search_queries": self._generate_search_queries(query),
            "evaluation_criteria": {
                "source_credibility": ["peer_reviewed", "official", "expert"],
                "data_quality": ["recent", "quantitative", "verifiable"],
                "relevance": ["direct", "contextual", "supporting"]
            },
            "timeline_seconds": min(query.timeout_seconds, 3600)
        }
        
        return plan
        
    def _generate_search_queries(self, query: ResearchQuery) -> List[str]:
        """Generate multiple search queries for comprehensive coverage"""
        base = query.rewritten_prompt or query.original_query
        
        # Extract key terms and generate variations
        queries = [
            base,
            f"{base} statistics data",
            f"{base} research studies",
            f"{base} expert analysis",
            f"{base} case studies examples",
            f"{base} trends forecast",
            f"{base} challenges solutions"
        ]
        
        return queries[:10]  # Limit to 10 queries


class DataGatheringAgent:
    """Agent for gathering data from multiple sources"""
    
    async def gather(self, query: ResearchQuery, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather data from multiple sources in parallel
        """
        gathered_data = {
            "sources": [],
            "raw_content": [],
            "metadata": {
                "total_sources": 0,
                "source_types": {},
                "gathering_errors": []
            }
        }
        
        # Simulate parallel data gathering
        tasks = []
        for search_query in plan.get("search_queries", []):
            tasks.append(self._search_web(search_query))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                gathered_data["metadata"]["gathering_errors"].append(str(result))
            else:
                gathered_data["sources"].extend(result)
                
        gathered_data["metadata"]["total_sources"] = len(gathered_data["sources"])
        
        return gathered_data
        
    async def _search_web(self, query: str) -> List[ResearchSource]:
        """Simulate web search (would use actual APIs in production)"""
        # Placeholder for actual web search implementation
        sources = []
        
        # Simulate finding sources
        for i in range(3):
            source = ResearchSource(
                url=f"https://example.com/article_{i}",
                title=f"Research on {query} - Source {i}",
                content=f"Detailed content about {query}...",
                source_type="web",
                credibility_score=0.8,
                relevance_score=0.9,
                timestamp=datetime.now().isoformat()
            )
            sources.append(source)
            
        await asyncio.sleep(0.1)  # Simulate API delay
        return sources


class AnalysisAgent:
    """Agent for analyzing gathered data"""
    
    async def analyze(self, data: Dict[str, Any], query: ResearchQuery) -> Dict[str, Any]:
        """
        Analyze gathered data for patterns, insights, and key findings
        """
        analysis = {
            "key_themes": [],
            "statistical_findings": {},
            "expert_opinions": [],
            "contradictions": [],
            "gaps": [],
            "confidence_scores": {}
        }
        
        # Analyze sources
        for source in data.get("sources", []):
            # Extract themes (simplified)
            themes = self._extract_themes(source.content)
            analysis["key_themes"].extend(themes)
            
            # Extract statistics
            stats = self._extract_statistics(source.content)
            analysis["statistical_findings"].update(stats)
            
        # Remove duplicates and rank by frequency
        analysis["key_themes"] = list(set(analysis["key_themes"]))
        
        return analysis
        
    def _extract_themes(self, content: str) -> List[str]:
        """Extract key themes from content"""
        # Simplified theme extraction
        themes = []
        keywords = ["impact", "trend", "challenge", "opportunity", "solution"]
        
        for keyword in keywords:
            if keyword.lower() in content.lower():
                themes.append(keyword)
                
        return themes
        
    def _extract_statistics(self, content: str) -> Dict[str, Any]:
        """Extract statistical data from content"""
        stats = {}
        
        # Simple pattern matching for numbers
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?%?', content)
        
        if numbers:
            stats["extracted_numbers"] = numbers[:5]  # Limit to 5
            
        return stats


class SynthesisAgent:
    """Agent for synthesizing findings"""
    
    async def synthesize(self, data: Dict[str, Any], query: ResearchQuery) -> List[ResearchFindings]:
        """
        Synthesize analyzed data into coherent findings
        """
        findings = []
        
        # Create main findings section
        main_finding = ResearchFindings(
            section_title="Primary Research Findings",
            content=f"Analysis of {query.original_query} reveals several key insights...",
            sources=[],  # Would be populated from actual sources
            confidence_level=0.85,
            key_insights=[
                "Key insight 1 based on multiple sources",
                "Key insight 2 supported by data",
                "Key insight 3 from expert analysis"
            ],
            data_points={
                "trend": "increasing",
                "impact_scale": "significant",
                "geographic_scope": "global"
            }
        )
        findings.append(main_finding)
        
        # Add thematic findings
        for theme in data.get("key_themes", [])[:3]:
            theme_finding = ResearchFindings(
                section_title=f"Analysis: {theme.capitalize()}",
                content=f"Detailed analysis of {theme} aspects...",
                sources=[],
                confidence_level=0.75,
                key_insights=[f"Insight related to {theme}"],
                data_points={}
            )
            findings.append(theme_finding)
            
        return findings


class ValidationAgent:
    """Agent for validating findings"""
    
    async def validate(self, findings: List[ResearchFindings], raw_data: Dict[str, Any]) -> List[ResearchFindings]:
        """
        Validate findings against raw data and check for consistency
        """
        validated_findings = []
        
        for finding in findings:
            # Check source credibility
            credibility_check = self._check_credibility(finding.sources)
            
            # Cross-reference claims
            cross_ref_score = self._cross_reference(finding.content, raw_data)
            
            # Adjust confidence based on validation
            finding.confidence_level *= (credibility_check * cross_ref_score)
            
            validated_findings.append(finding)
            
        return validated_findings
        
    def _check_credibility(self, sources: List[ResearchSource]) -> float:
        """Check average credibility of sources"""
        if not sources:
            return 0.5
            
        avg_credibility = sum(s.credibility_score for s in sources) / len(sources)
        return avg_credibility
        
    def _cross_reference(self, content: str, raw_data: Dict[str, Any]) -> float:
        """Cross-reference claims with raw data"""
        # Simplified cross-referencing
        return 0.9  # Placeholder


class ReportGenerationAgent:
    """Agent for generating final research reports"""
    
    async def generate(
        self,
        query: ResearchQuery,
        findings: List[ResearchFindings],
        raw_data: Dict[str, Any],
        duration: float
    ) -> ResearchReport:
        """
        Generate comprehensive research report
        """
        # Generate executive summary
        exec_summary = self._generate_executive_summary(query, findings)
        
        # Extract methodology
        methodology = self._describe_methodology(query, raw_data)
        
        # Identify limitations
        limitations = self._identify_limitations(query, findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        # Compile citations
        citations = self._compile_citations(findings)
        
        # Calculate overall confidence
        avg_confidence = sum(f.confidence_level for f in findings) / len(findings) if findings else 0
        
        report = ResearchReport(
            query=query,
            executive_summary=exec_summary,
            findings=findings,
            methodology=methodology,
            limitations=limitations,
            recommendations=recommendations,
            total_sources_analyzed=raw_data.get("metadata", {}).get("total_sources", 0),
            research_duration_seconds=duration,
            confidence_score=avg_confidence,
            citations=citations,
            raw_data=raw_data if query.analysis_depth == "exhaustive" else None
        )
        
        return report
        
    def _generate_executive_summary(self, query: ResearchQuery, findings: List[ResearchFindings]) -> str:
        """Generate executive summary"""
        summary = f"""
        Research Summary: {query.original_query}
        
        This comprehensive research analyzed {len(findings)} key areas and identified 
        significant patterns and insights. The research reveals important trends and 
        provides actionable recommendations based on data-driven analysis.
        
        Key Findings:
        """
        
        for finding in findings[:3]:
            summary += f"\n- {finding.section_title}: {finding.key_insights[0] if finding.key_insights else 'See details'}"
            
        return summary
        
    def _describe_methodology(self, query: ResearchQuery, raw_data: Dict[str, Any]) -> str:
        """Describe research methodology"""
        return f"""
        Research Methodology:
        
        1. Data Collection: Gathered from {len(query.data_sources)} source types
        2. Analysis Approach: {query.analysis_depth} analysis
        3. Validation: Cross-referenced findings across multiple sources
        4. Synthesis: Integrated findings into coherent insights
        5. Quality Assurance: Validated against credibility criteria
        """
        
    def _identify_limitations(self, query: ResearchQuery, findings: List[ResearchFindings]) -> List[str]:
        """Identify research limitations"""
        limitations = [
            "Time constraints may limit comprehensiveness",
            "Some sources may have inherent biases",
            "Rapidly evolving topics may outdated quickly"
        ]
        
        if query.max_sources < 50:
            limitations.append(f"Limited to {query.max_sources} sources")
            
        return limitations
        
    def _generate_recommendations(self, findings: List[ResearchFindings]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for finding in findings:
            if finding.confidence_level > 0.7:
                rec = f"Based on {finding.section_title}: Consider implementing strategies to address identified patterns"
                recommendations.append(rec)
                
        return recommendations[:5]  # Limit to 5 recommendations
        
    def _compile_citations(self, findings: List[ResearchFindings]) -> List[Dict[str, Any]]:
        """Compile all citations"""
        citations = []
        
        for finding in findings:
            for source in finding.sources:
                citation = {
                    "title": source.title,
                    "url": source.url,
                    "type": source.source_type,
                    "accessed": source.timestamp
                }
                citations.append(citation)
                
        return citations


# Convenience function for easy use
async def deep_research(
    query: str,
    skip_clarification: bool = False,
    data_sources: Optional[List[str]] = None,
    **kwargs
) -> ResearchReport:
    """
    Conduct deep research on a given query
    
    Args:
        query: Research question or topic
        skip_clarification: Skip clarification if query is already detailed
        data_sources: List of data sources to use
        **kwargs: Additional configuration options
        
    Returns:
        Comprehensive ResearchReport
    """
    orchestrator = DeepResearchOrchestrator()
    report = await orchestrator.conduct_research(
        query=query,
        skip_clarification=skip_clarification,
        data_sources=data_sources,
        **kwargs
    )
    return report


# Example usage
if __name__ == "__main__":
    async def main():
        # Example research query
        query = "What is the economic impact of AI on healthcare systems globally?"
        
        # Conduct research
        report = await deep_research(
            query=query,
            skip_clarification=False,
            data_sources=["web", "academic", "news"],
            analysis_depth="comprehensive",
            max_sources=50
        )
        
        # Print executive summary
        print("=" * 80)
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        print(report.executive_summary)
        
        # Print findings
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)
        for finding in report.findings:
            print(f"\n{finding.section_title}")
            print(f"Confidence: {finding.confidence_level:.2%}")
            print(f"Content: {finding.content[:200]}...")
            
        # Print methodology
        print("\n" + "=" * 80)
        print("METHODOLOGY")
        print("=" * 80)
        print(report.methodology)
        
        # Print stats
        print("\n" + "=" * 80)
        print("RESEARCH STATISTICS")
        print("=" * 80)
        print(f"Sources Analyzed: {report.total_sources_analyzed}")
        print(f"Research Duration: {report.research_duration_seconds:.1f} seconds")
        print(f"Overall Confidence: {report.confidence_score:.2%}")
    
    # Run the example
    asyncio.run(main())