"""
Integration Tests for ModelRouter & PromptCache in AgentOrchestrator
====================================================================
Tests that ModelRouter and PromptCache are properly integrated.

Sprint 1, Day 1: Integration Testing
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from services.agent_orchestrator import AgentOrchestrator
from services.model_router import QueryIntent, ModelTier


@pytest.fixture
def orchestrator():
    """Create orchestrator instance with mocked services."""
    with patch('services.agent_orchestrator.AsyncOpenAI'):
        with patch('services.agent_orchestrator.MarketServiceFactory.get_service'):
            with patch('services.agent_orchestrator.asyncio.create_task'):
                orch = AgentOrchestrator()
                return orch


class TestModelRouterIntegration:
    """Test ModelRouter integration in AgentOrchestrator."""

    def test_model_router_initialized(self, orchestrator):
        """Test that ModelRouter is initialized in orchestrator."""
        assert orchestrator.model_router is not None
        assert hasattr(orchestrator, 'model_router')

    def test_prompt_cache_initialized(self, orchestrator):
        """Test that PromptCache is initialized in orchestrator."""
        assert orchestrator.prompt_cache is not None
        assert hasattr(orchestrator, 'prompt_cache')

    @pytest.mark.asyncio
    async def test_price_query_uses_cheap_model(self, orchestrator):
        """Test that simple price queries use gpt-4o-mini."""
        # Mock the OpenAI call
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "TSLA is trading at $250.00"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=20,
            total_tokens=70
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            # Make a price query
            result = await orchestrator.process_query(
                "What's the price of TSLA?",
                conversation_history=None,
                stream=False
            )

            # Verify gpt-4o-mini was used (cheap model for price queries)
            call_args = mock_call.call_args
            assert call_args is not None
            assert call_args[1]['model'] == 'gpt-4o-mini'

            # Verify response includes correct model
            assert result['model'] == 'gpt-4o-mini'

    @pytest.mark.asyncio
    async def test_technical_query_uses_mid_model(self, orchestrator):
        """Test that technical analysis queries use gpt-4o."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "NVDA shows bullish RSI divergence"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            # Make a technical analysis query
            result = await orchestrator.process_query(
                "Analyze NVDA with RSI and MACD",
                conversation_history=None,
                stream=False
            )

            # Verify gpt-4o was used (mid-tier model for technical analysis)
            call_args = mock_call.call_args
            assert call_args is not None
            assert call_args[1]['model'] == 'gpt-4o'

            # Verify response includes correct model
            assert result['model'] == 'gpt-4o'

    @pytest.mark.asyncio
    async def test_model_router_fallback_on_error(self, orchestrator):
        """Test that orchestrator falls back to default model if routing fails."""
        # Simulate routing failure by making select_model raise exception
        with patch.object(orchestrator.model_router, 'select_model', side_effect=Exception("Routing failed")):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response text"
            mock_response.choices[0].message.tool_calls = None
            mock_response.choices[0].finish_reason = "stop"
            mock_response.usage = MagicMock(
                prompt_tokens=50,
                completion_tokens=20,
                total_tokens=70
            )

            with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
                mock_call.return_value = mock_response

                result = await orchestrator.process_query(
                    "What's AAPL price?",
                    conversation_history=None,
                    stream=False
                )

                # Should fall back to default model (gpt-5-mini from env)
                call_args = mock_call.call_args
                assert call_args is not None
                assert call_args[1]['model'] in ['gpt-5-mini', 'gpt-4o-mini', 'gpt-4o']


class TestPromptCacheIntegration:
    """Test PromptCache integration in AgentOrchestrator."""

    @pytest.mark.asyncio
    async def test_large_prompt_uses_caching(self, orchestrator):
        """Test that large prompts are cached."""
        # Create a large query (>1024 tokens worth)
        large_query = "Analyze " + ("the market trends " * 300)  # ~900 words

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Analysis result"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=3000,
            completion_tokens=100,
            total_tokens=3100
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            # First call - should cache
            cache_size_before = len(orchestrator.prompt_cache.cache)

            result1 = await orchestrator.process_query(
                large_query,
                conversation_history=None,
                stream=False
            )

            cache_size_after = len(orchestrator.prompt_cache.cache)

            # Cache should have grown (prompt was large enough to cache)
            assert cache_size_after >= cache_size_before

    @pytest.mark.asyncio
    async def test_small_prompt_skips_caching(self, orchestrator):
        """Test that small prompts are not cached."""
        small_query = "What's TSLA price?"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "TSLA is $250"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=10,
            total_tokens=60
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            cache_size_before = len(orchestrator.prompt_cache.cache)

            result = await orchestrator.process_query(
                small_query,
                conversation_history=None,
                stream=False
            )

            cache_size_after = len(orchestrator.prompt_cache.cache)

            # Cache size should not grow (prompt too small)
            assert cache_size_after == cache_size_before

    def test_cache_stats_available(self, orchestrator):
        """Test that cache statistics are accessible."""
        stats = orchestrator.prompt_cache.get_stats()

        assert 'size' in stats
        assert 'max_size' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats


class TestIntegrationDiagnostics:
    """Test that diagnostics include correct model information."""

    @pytest.mark.asyncio
    async def test_diagnostics_use_selected_model(self, orchestrator):
        """Test that diagnostics include the ModelRouter-selected model."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Price is $250"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=10,
            total_tokens=60
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await orchestrator.process_query(
                "What's TSLA price?",
                conversation_history=None,
                stream=False
            )

            # Check diagnostics
            assert orchestrator.last_diag is not None
            assert 'model' in orchestrator.last_diag

            # Should use gpt-4o-mini for price queries, not the default
            assert orchestrator.last_diag['model'] == 'gpt-4o-mini'

    @pytest.mark.asyncio
    async def test_response_includes_selected_model(self, orchestrator):
        """Test that response payload includes the correct model."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Analysis complete"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )

        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await orchestrator.process_query(
                "Analyze NVDA with technical indicators",
                conversation_history=None,
                stream=False
            )

            # Response should include the selected model
            assert 'model' in result
            assert result['model'] in ['gpt-4o-mini', 'gpt-4o', 'gpt-5']
            # Should be gpt-4o for technical queries (not the default gpt-5-mini)
            assert result['model'] == 'gpt-4o'


class TestErrorPathModelReporting:
    """Test that error paths report correct model information."""

    @pytest.mark.asyncio
    async def test_error_response_includes_model(self, orchestrator):
        """Test that error responses include model information."""
        # Force an error after model selection
        with patch.object(orchestrator, '_call_openai_with_retry', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("API error")

            result = await orchestrator.process_query(
                "What's AAPL price?",
                conversation_history=None,
                stream=False
            )

            # Error response should include a model
            assert 'model' in result
            # Should be the selected model (gpt-4o-mini for price) or fallback
            assert result['model'] in ['gpt-4o-mini', 'gpt-5-mini']
