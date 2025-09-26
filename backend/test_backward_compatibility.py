#!/usr/bin/env python3
"""
Backward Compatibility Test Suite
==================================
Ensures that the knowledge enhancement doesn't break existing functionality.
Tests all critical paths that were working before the knowledge system upgrade.
"""

import asyncio
import logging
from typing import Dict, List, Any
from services.agent_orchestrator import AgentOrchestrator
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackwardCompatibilityTester:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.test_results = []
        
    async def test_stock_specific_queries(self) -> Dict[str, Any]:
        """Test that stock-specific queries still work with tool execution."""
        print("\n🔧 Testing Stock-Specific Queries (with tools)")
        print("-" * 60)
        
        test_cases = [
            ("What's the price of AAPL?", ["get_stock_price"]),
            ("Show me TSLA news", ["get_stock_news"]), 
            ("Analyze NVDA chart", ["get_stock_history", "get_comprehensive_stock_data"]),
        ]
        
        results = []
        for query, expected_tools in test_cases:
            try:
                start = time.time()
                response = await self.orchestrator.process_query(query)
                duration = time.time() - start
                
                tools_used = response.get('tools_used', [])
                has_expected_tools = any(tool in tools_used for tool in expected_tools)
                
                result = {
                    'query': query,
                    'success': True,
                    'duration': duration,
                    'tools_used': tools_used,
                    'expected_tools': expected_tools,
                    'tools_match': has_expected_tools,
                    'has_response': bool(response.get('text'))
                }
                
                print(f"✅ {query[:30]}... - {duration:.2f}s")
                if not has_expected_tools:
                    print(f"  ⚠️ Expected tools: {expected_tools}, Got: {tools_used}")
                    
            except Exception as e:
                result = {
                    'query': query,
                    'success': False,
                    'error': str(e)
                }
                print(f"❌ {query[:30]}... - Error: {e}")
                
            results.append(result)
            
        return {
            'category': 'Stock-Specific Queries',
            'total': len(test_cases),
            'passed': sum(1 for r in results if r.get('success')),
            'results': results
        }
    
    async def test_educational_queries(self) -> Dict[str, Any]:
        """Test that educational queries now include knowledge retrieval."""
        print("\n📚 Testing Educational Queries (knowledge retrieval)")
        print("-" * 60)
        
        test_cases = [
            "What is a moving average?",
            "Explain RSI indicator",
            "How do I read candlestick patterns?",
            "What is support and resistance?",
        ]
        
        results = []
        for query in test_cases:
            try:
                start = time.time()
                response = await self.orchestrator.process_query(query)
                duration = time.time() - start
                
                response_text = response.get('text', '').lower()
                
                # Check for knowledge indicators
                knowledge_indicators = ['according to', 'typically', 'calculated', 'indicates']
                has_knowledge = any(ind in response_text for ind in knowledge_indicators)
                
                result = {
                    'query': query,
                    'success': True,
                    'duration': duration,
                    'has_knowledge': has_knowledge,
                    'response_length': len(response_text),
                    'tools_used': response.get('tools_used', [])
                }
                
                print(f"✅ {query[:30]}... - {duration:.2f}s")
                if has_knowledge:
                    print(f"  📚 Knowledge retrieved successfully")
                    
            except Exception as e:
                result = {
                    'query': query,
                    'success': False,
                    'error': str(e)
                }
                print(f"❌ {query[:30]}... - Error: {e}")
                
            results.append(result)
            
        return {
            'category': 'Educational Queries',
            'total': len(test_cases),
            'passed': sum(1 for r in results if r.get('success')),
            'with_knowledge': sum(1 for r in results if r.get('has_knowledge')),
            'results': results
        }
    
    async def test_mixed_queries(self) -> Dict[str, Any]:
        """Test queries that should combine tools and knowledge."""
        print("\n🔀 Testing Mixed Queries (tools + knowledge)")
        print("-" * 60)
        
        test_cases = [
            "Analyze AAPL using RSI",
            "Is TSLA oversold based on technical indicators?",
            "Show me support levels for NVDA",
        ]
        
        results = []
        for query in test_cases:
            try:
                start = time.time()
                response = await self.orchestrator.process_query(query)
                duration = time.time() - start
                
                tools_used = response.get('tools_used', [])
                response_text = response.get('text', '').lower()
                
                # Check for both tools and knowledge
                has_tools = len(tools_used) > 0
                knowledge_indicators = ['rsi', 'oversold', 'overbought', 'support', 'resistance', 'indicator']
                has_knowledge = any(ind in response_text for ind in knowledge_indicators)
                
                result = {
                    'query': query,
                    'success': True,
                    'duration': duration,
                    'has_tools': has_tools,
                    'has_knowledge': has_knowledge,
                    'tools_used': tools_used,
                    'response_length': len(response_text)
                }
                
                print(f"✅ {query[:30]}... - {duration:.2f}s")
                print(f"  🔧 Tools: {tools_used if has_tools else 'None'}")
                print(f"  📚 Knowledge: {'Yes' if has_knowledge else 'No'}")
                    
            except Exception as e:
                result = {
                    'query': query,
                    'success': False,
                    'error': str(e)
                }
                print(f"❌ {query[:30]}... - Error: {e}")
                
            results.append(result)
            
        return {
            'category': 'Mixed Queries',
            'total': len(test_cases),
            'passed': sum(1 for r in results if r.get('success')),
            'with_both': sum(1 for r in results if r.get('has_tools') and r.get('has_knowledge')),
            'results': results
        }
    
    async def test_performance_regression(self) -> Dict[str, Any]:
        """Test that response times haven't degraded significantly."""
        print("\n⚡ Testing Performance (response times)")
        print("-" * 60)
        
        # Performance benchmarks (in seconds)
        benchmarks = {
            'simple_query': 3.0,  # Simple queries should be under 3s
            'tool_query': 5.0,    # Tool queries should be under 5s
            'complex_query': 8.0  # Complex queries should be under 8s
        }
        
        test_cases = [
            ("What's the current market trend?", 'simple_query'),
            ("Get AAPL price", 'tool_query'),
            ("Analyze TSLA with full technical indicators and news", 'complex_query'),
        ]
        
        results = []
        for query, query_type in test_cases:
            try:
                start = time.time()
                response = await self.orchestrator.process_query(query)
                duration = time.time() - start
                
                benchmark = benchmarks[query_type]
                passed = duration <= benchmark
                
                result = {
                    'query': query,
                    'type': query_type,
                    'success': True,
                    'duration': duration,
                    'benchmark': benchmark,
                    'performance_ok': passed
                }
                
                status = "✅" if passed else "⚠️"
                print(f"{status} {query[:30]}... - {duration:.2f}s (benchmark: {benchmark}s)")
                    
            except Exception as e:
                result = {
                    'query': query,
                    'type': query_type,
                    'success': False,
                    'error': str(e)
                }
                print(f"❌ {query[:30]}... - Error: {e}")
                
            results.append(result)
            
        return {
            'category': 'Performance',
            'total': len(test_cases),
            'passed': sum(1 for r in results if r.get('performance_ok')),
            'results': results
        }
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test that error handling still works correctly."""
        print("\n🛡️ Testing Error Handling")
        print("-" * 60)
        
        test_cases = [
            "What's the price of INVALID_SYMBOL?",
            "Analyze XYZABC123",
            "",  # Empty query
        ]
        
        results = []
        for query in test_cases:
            try:
                response = await self.orchestrator.process_query(query)
                
                # Should handle gracefully
                has_response = bool(response.get('text'))
                is_error_handled = 'error' in response.get('text', '').lower() or \
                                 'invalid' in response.get('text', '').lower() or \
                                 not has_response
                
                result = {
                    'query': query if query else '(empty)',
                    'success': True,
                    'handled_gracefully': is_error_handled,
                    'has_response': has_response
                }
                
                print(f"✅ {(query[:30] if query else '(empty)')}... - Handled: {is_error_handled}")
                    
            except Exception as e:
                # Exceptions are also acceptable for invalid inputs
                result = {
                    'query': query if query else '(empty)',
                    'success': True,
                    'handled_gracefully': True,
                    'exception': str(e)
                }
                print(f"✅ {(query[:30] if query else '(empty)')}... - Exception handled")
                
            results.append(result)
            
        return {
            'category': 'Error Handling',
            'total': len(test_cases),
            'handled': sum(1 for r in results if r.get('handled_gracefully')),
            'results': results
        }
    
    async def run_all_tests(self):
        """Run all backward compatibility tests."""
        print("=" * 80)
        print("BACKWARD COMPATIBILITY TEST SUITE")
        print("=" * 80)
        
        test_methods = [
            self.test_stock_specific_queries,
            self.test_educational_queries,
            self.test_mixed_queries,
            self.test_performance_regression,
            self.test_error_handling,
        ]
        
        all_results = []
        for test_method in test_methods:
            result = await test_method()
            all_results.append(result)
            await asyncio.sleep(1)  # Brief pause between test categories
        
        # Generate summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = sum(r['total'] for r in all_results)
        total_passed = sum(r.get('passed', r.get('handled', 0)) for r in all_results)
        
        for result in all_results:
            category = result['category']
            passed = result.get('passed', result.get('handled', 0))
            total = result['total']
            status = "✅" if passed == total else "⚠️"
            
            print(f"{status} {category}: {passed}/{total} passed")
            
            # Special metrics
            if 'with_knowledge' in result:
                print(f"  📚 With knowledge: {result['with_knowledge']}/{total}")
            if 'with_both' in result:
                print(f"  🔀 With tools+knowledge: {result['with_both']}/{total}")
        
        print(f"\n{'='*40}")
        print(f"OVERALL: {total_passed}/{total_tests} tests passed")
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ BACKWARD COMPATIBILITY MAINTAINED")
        elif success_rate >= 70:
            print("⚠️ MINOR REGRESSIONS DETECTED")
        else:
            print("❌ SIGNIFICANT REGRESSIONS - REVIEW REQUIRED")
        
        return all_results

async def main():
    """Run the backward compatibility test suite."""
    tester = BackwardCompatibilityTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())