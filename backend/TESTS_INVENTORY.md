# Backend Test Inventory
**Generated:** 2025-11-08
**Total Tests:** 92 files (88 root, 4 organized)

## Summary

| Category | Count | Location |
|----------|-------|----------|
| Organized Tests | 4 | `tests/` |
| Root Tests | 88 | `.` (backend root) |
| **Total** | **92** | - |

---

## Organized Tests (`tests/` directory)

### 1. Pattern System Tests
| File | Purpose | Dependencies | Est. Duration |
|------|---------|--------------|---------------|
| `tests/test_pattern_library.py` | Pattern library functionality | Supabase | 5-10s |
| `tests/test_pattern_metadata.py` | Pattern metadata operations | Supabase | 5-10s |

### 2. Phase Regression Tests
| File | Purpose | Dependencies | Est. Duration |
|------|---------|--------------|---------------|
| `tests/test_phase5_ml_flow.py` | ML flow and model registry | ML models | 10-20s |
| `tests/test_phase5_regression.py` | Phase 5 regression suite | Full stack | 20-30s |

**Run Command:**
```bash
pytest tests/  # Run all organized tests
pytest tests/test_pattern_library.py -v  # Single file
```

---

## Root Tests (backend root directory)

### Agent & Orchestrator Tests (16 files)
Core agent functionality and orchestration logic.

| File | Purpose | OpenAI | Alpaca | Duration |
|------|---------|--------|--------|----------|
| `test_agent_analysis.py` | Agent analysis capabilities | ✅ | ✅ | 10-15s |
| `test_agent_analysis_simple.py` | Simplified agent analysis | ✅ | - | 5-10s |
| `test_agent_capabilities.py` | Agent capabilities testing | ✅ | - | 10-15s |
| `test_agent_knowledge.py` | Knowledge retrieval | ✅ | - | 10-20s |
| `test_agent_performance_live.py` | Live performance testing | ✅ | ✅ | 15-30s |
| `test_agent_questions.py` | Question answering | ✅ | - | 10-15s |
| `test_agent_sdk_aapl.py` | SDK with AAPL symbol | ✅ | ✅ | 10-15s |
| `test_agent_sdk_focused.py` | Focused SDK testing | ✅ | - | 5-10s |
| `test_agent_simple.py` | Simple agent tests | ✅ | - | 5-10s |
| `test_final_agent.py` | Final agent integration | ✅ | ✅ | 15-20s |
| `test_orchestrator_debug.py` | Orchestrator debugging | ✅ | - | 5-10s |
| `test_symbol_resolution_agent.py` | Symbol resolution via agent | ✅ | ✅ | 10-15s |
| `test_symbol_resolution_fallback.py` | Symbol resolution fallback | - | ✅ | 5-10s |
| `test_new_trader_experience.py` | Trader UX testing | ✅ | ✅ | 15-20s |
| `test_user_experience.py` | User experience flows | ✅ | - | 10-15s |
| `test_trader_scenarios.py` | Trading scenarios | ✅ | ✅ | 20-30s |

**Run Examples:**
```bash
python test_agent_simple.py           # Quick agent test
python test_agent_performance_live.py # Performance benchmark
python test_orchestrator_debug.py     # Debug orchestrator
```

### Chart Control Tests (4 files)
Chart command processing and navigation.

| File | Purpose | OpenAI | Duration |
|------|---------|--------|----------|
| `test_chart_control_simple.py` | Basic chart control | - | 2-5s |
| `test_chart_control_tools.py` | Chart tool schemas | - | 2-5s |
| `test_chart_navigation.py` | Chart navigation flows | ✅ | 5-10s |
| `test_manual_chart_commands.py` | Manual command testing | - | 2-5s |

**Run Examples:**
```bash
python test_chart_control_tools.py  # Verify tool schemas
python test_chart_navigation.py     # Test navigation
```

### OpenAI Integration Tests (14 files)
OpenAI API, Realtime API, and responses API testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_anthropic_quick.py` | Anthropic API quick test | Anthropic | 5-10s |
| `test_openai_connection.py` | OpenAI connection test | OpenAI | 2-5s |
| `test_openai_models.py` | OpenAI models testing | OpenAI | 5-10s |
| `test_openai_realtime.py` | Realtime API testing | OpenAI | 10-15s |
| `test_openai_websocket_direct.py` | Direct WebSocket test | OpenAI | 10-15s |
| `test_openai_workflow.py` | Workflow testing | OpenAI | 10-15s |
| `test_responses_api.py` | Responses API test | OpenAI | 5-10s |
| `test_responses_api_actual.py` | Actual responses API | OpenAI | 5-10s |
| `test_responses_api_availability.py` | API availability check | OpenAI | 2-5s |
| `test_responses_api_e2e.py` | E2E responses API | OpenAI | 10-15s |
| `test_responses_api_fix.py` | Responses API fixes | OpenAI | 5-10s |
| `test_responses_fix.py` | Response fixes | OpenAI | 5-10s |
| `test_responses_format.py` | Response formatting | OpenAI | 5-10s |
| `test_responses_text_extraction.py` | Text extraction | OpenAI | 5-10s |

**Run Examples:**
```bash
python test_openai_connection.py    # Quick connection test
python test_openai_realtime.py      # Realtime API
python test_responses_api_e2e.py    # Full responses API flow
```

### Voice & Relay Tests (7 files)
Voice assistant and OpenAI Realtime relay testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_voice_assistant_comprehensive.py` | Comprehensive voice test | OpenAI + ElevenLabs | 20-30s |
| `test_voice_openai_realtime.py` | OpenAI Realtime voice | OpenAI | 15-20s |
| `test_voice_relay_sessions.py` | Relay session management | OpenAI | 10-15s |
| `test_voice_relay_simple.py` | Simple relay test | OpenAI | 5-10s |
| `test_voice_ta_complete.py` | Voice + TA integration | OpenAI + Alpaca | 20-30s |
| `test_relay_tools.py` | Relay tool testing | OpenAI | 5-10s |
| `test_websocket_endpoint.py` | WebSocket endpoint | - | 5-10s |

**Run Examples:**
```bash
python test_voice_relay_simple.py      # Quick relay test
python test_voice_relay_sessions.py    # Session management
```

### Performance & Latency Tests (4 files)
Performance benchmarking and latency measurement.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_current_performance.py` | Current performance baseline | OpenAI + Alpaca | 30-60s |
| `test_latency.py` | Detailed latency analysis | OpenAI | 20-30s |
| `test_simple_latency.py` | Simple latency check | OpenAI | 10-15s |
| `test_streaming.py` | Streaming performance | OpenAI | 15-20s |

**Run Examples:**
```bash
python test_current_performance.py  # Full performance suite
python test_simple_latency.py       # Quick latency check
```

### Technical Analysis Tests (6 files)
Technical indicators, levels, and pattern detection.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_level_calculations.py` | TA level calculations | - | 2-5s |
| `test_pattern_detection.py` | Pattern detection logic | OpenAI | 10-15s |
| `test_tech_quick.py` | Quick TA test | Alpaca | 5-10s |
| `test_technical_analysis_comprehensive.py` | Comprehensive TA | Alpaca | 15-20s |
| `test_technical_indicators.py` | Indicator calculations | - | 5-10s |
| `test_trading_levels.py` | Trading level logic | Alpaca | 10-15s |

**Run Examples:**
```bash
python test_level_calculations.py  # Test calculations
python test_technical_analysis_comprehensive.py  # Full TA suite
```

### Trading & Market Tests (5 files)
Market data, trading scenarios, and swing trading.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_market_overview.py` | Market overview endpoint | Alpaca | 5-10s |
| `test_swing_trade.py` | Swing trading logic | Alpaca | 10-15s |
| `test_trader_quick.py` | Quick trader test | Alpaca | 5-10s |
| `test_production_ask.py` | Production /ask endpoint | OpenAI + Alpaca | 10-15s |
| `test_ask_debug.py` | Debug /ask endpoint | OpenAI | 5-10s |

**Run Examples:**
```bash
python test_market_overview.py  # Test market data
python test_swing_trade.py      # Swing trading
```

### MCP Integration Tests (2 files)
Model Context Protocol server testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_mcp_dual_transport.py` | Dual transport (WS + HTTP) | MCP servers | 10-15s |
| `test_mcp_http_endpoint.py` | HTTP MCP endpoint | MCP servers | 5-10s |

**Run Examples:**
```bash
python test_mcp_http_endpoint.py  # Test HTTP endpoint
python test_mcp_dual_transport.py  # Test both transports
```

### Computer Use Tests (9 files)
Anthropic Computer Use API testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_computer_click.py` | Click interaction | Anthropic | 10-15s |
| `test_computer_use_api.py` | Computer Use API | Anthropic | 10-15s |
| `test_computer_use_debug.py` | Debug computer use | Anthropic | 5-10s |
| `test_computer_use_docker.py` | Docker integration | Anthropic + Docker | 20-30s |
| `test_computer_use_fixed.py` | Fixed implementation | Anthropic | 10-15s |
| `test_computer_use_minimal.py` | Minimal test case | Anthropic | 5-10s |
| `test_computer_use_setup.py` | Setup verification | Anthropic | 2-5s |
| `test_computer_use_simple.py` | Simple test | Anthropic | 5-10s |
| `test_cua_now.py` | Current CUA status | Anthropic | 5-10s |

**Run Examples:**
```bash
python test_computer_use_simple.py  # Quick test
python test_computer_use_api.py     # Full API test
```

### Playwright Tests (3 files)
Browser automation via Playwright MCP.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_playwright_demo.py` | Playwright demo | Playwright MCP | 10-15s |
| `test_playwright_simple.py` | Simple Playwright test | Playwright MCP | 5-10s |
| `test_headless.py` | Headless browser test | Playwright | 10-15s |

**Run Examples:**
```bash
python test_playwright_simple.py  # Quick browser test
```

### Regression Tests (4 files)
Multi-phase regression testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_api_regression.py` | API regression suite | OpenAI + Alpaca | 20-30s |
| `test_phase3_regression.py` | Phase 3 regression | Full stack | 15-20s |
| `test_phase4_regression.py` | Phase 4 regression | Full stack | 15-20s |
| `test_backward_compatibility.py` | Backward compatibility | OpenAI | 10-15s |

**Run Examples:**
```bash
python test_api_regression.py      # API regressions
python test_phase3_regression.py   # Phase 3 checks
```

### Knowledge & Vector Tests (5 files)
Knowledge retrieval and vector database testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_knowledge_retrieval.py` | Knowledge retrieval | OpenAI + Supabase | 10-15s |
| `test_vector_integration.py` | Vector DB integration | Supabase | 10-15s |
| `test_embedding_direct.py` | Direct embedding API | OpenAI | 5-10s |
| `test_embeddings_access.py` | Embeddings access | OpenAI | 5-10s |
| `test_deep_research.py` | Deep research flows | OpenAI + Search | 20-30s |

**Run Examples:**
```bash
python test_knowledge_retrieval.py  # Test retrieval
python test_vector_integration.py   # Vector DB
```

### Data Extraction & Enhancement Tests (4 files)
Data extraction and training enhancement.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_enhanced_extraction.py` | Enhanced extraction | OpenAI | 10-15s |
| `test_enhanced_training.py` | Training enhancements | OpenAI | 15-20s |
| `test_extraction_quick.py` | Quick extraction test | OpenAI | 5-10s |
| `test_structured_summary.py` | Structured summaries | OpenAI | 10-15s |

**Run Examples:**
```bash
python test_extraction_quick.py     # Quick extraction
python test_enhanced_extraction.py  # Full extraction
```

### Formatting & Display Tests (3 files)
Response formatting and display logic.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_formatter_simple.py` | Simple formatter | - | 2-5s |
| `test_ideal_formatter.py` | Ideal formatter | OpenAI | 5-10s |
| `test_bounded_insights.py` | Bounded insights | OpenAI | 5-10s |

**Run Examples:**
```bash
python test_formatter_simple.py  # Test formatting
python test_ideal_formatter.py   # Ideal format
```

### Integration & System Tests (8 files)
Full system integration testing.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_full_integration.py` | Full integration test | Full stack | 30-60s |
| `test_full_loop.py` | Complete loop test | Full stack | 20-30s |
| `test_comprehensive_suite.py` | Comprehensive suite | Full stack | 40-60s |
| `test_simple_interaction.py` | Simple interaction | OpenAI | 5-10s |
| `test_conversation_debug.py` | Conversation debugging | OpenAI | 10-15s |
| `test_websockets_direct.py` | Direct WebSocket | - | 5-10s |
| `test_supabase_session.py` | Supabase sessions | Supabase | 5-10s |
| `test_token_limits.py` | Token limit handling | OpenAI | 10-15s |

**Run Examples:**
```bash
python test_simple_interaction.py  # Quick interaction
python test_full_integration.py    # Full integration
```

### Miscellaneous Tests (7 files)
Various utility and configuration tests.

| File | Purpose | Requires | Duration |
|------|---------|----------|----------|
| `test_correct_panel.py` | Panel selection | - | 2-5s |
| `test_correct_tool_format.py` | Tool format validation | - | 2-5s |
| `test_find_panels.py` | Panel discovery | - | 2-5s |
| `test_tool_configuration.py` | Tool config testing | - | 2-5s |
| `test_full_responses_api.py` | Full responses API | OpenAI | 10-15s |
| `test_openai_computer_use.py` | OpenAI + Computer Use | OpenAI + Anthropic | 15-20s |

**Run Examples:**
```bash
python test_tool_configuration.py  # Tool config
python test_correct_tool_format.py # Tool format
```

---

## Test Execution Strategy

### Quick Smoke Test (5-10 minutes)
Essential tests to verify core functionality.

```bash
# Backend core
python test_agent_simple.py
python test_chart_control_tools.py
python test_openai_connection.py

# Organized tests
pytest tests/test_pattern_library.py -v
```

### Standard Test Run (20-30 minutes)
Comprehensive test coverage.

```bash
# All organized tests
pytest tests/ -v

# Core agent tests
python test_agent_simple.py
python test_agent_capabilities.py
python test_orchestrator_debug.py

# Chart control
python test_chart_control_tools.py
python test_chart_navigation.py

# OpenAI integration
python test_openai_connection.py
python test_openai_models.py
python test_responses_api.py

# Performance
python test_simple_latency.py
```

### Full Test Suite (1-2 hours)
All tests including integration and performance.

```bash
# Organized tests
pytest tests/ -v --cov

# Run all root tests (may take 1-2 hours)
for test in test_*.py; do
    echo "Running $test..."
    python "$test" || echo "FAILED: $test"
done
```

### Performance Baseline (30-60 minutes)
Dedicated performance and latency testing.

```bash
python test_current_performance.py
python test_latency.py
python test_simple_latency.py
python test_streaming.py
python test_agent_performance_live.py
```

---

## Dependencies Summary

| Dependency | Test Count | Purpose |
|------------|------------|---------|
| OpenAI API | ~60 | LLM calls, function calling, embeddings |
| Alpaca API | ~25 | Market data, stock prices |
| Anthropic API | ~10 | Claude, Computer Use |
| Supabase | ~8 | Vector DB, patterns, sessions |
| MCP Servers | ~5 | Market MCP, Alpaca MCP |
| Playwright | ~3 | Browser automation |
| ElevenLabs | ~2 | Voice synthesis |
| None (Unit tests) | ~15 | Pure logic, no external deps |

---

## Known Issues & Notes

### Test Organization
- ✅ 4 tests in `tests/` directory (well-organized)
- ⚠️ 88 tests in root (works but cluttered)
- 📝 Recommendation: Gradually migrate to `tests/` subdirectories

### Missing Test Categories
- ❌ No frontend unit tests (only E2E Playwright)
- ❌ No chart command E2E tests
- ❌ No WebSocket stress tests
- ❌ No quota exhaustion handling tests

### Test Infrastructure Gaps
- ❌ No CI/CD pipeline configuration
- ❌ No test badges/status reporting
- ❌ No automated performance regression detection
- ❌ No test coverage reporting to external service

---

## Next Steps (Phase 1)

1. **Run Full Test Suite** - Execute all tests, document results
2. **Create Test Categories** - Organize into logical groups
3. **Add Missing Tests** - Frontend, E2E chart commands
4. **Setup CI/CD** - GitHub Actions for automated testing
5. **Coverage Reporting** - Integrate with Codecov or similar
6. **Performance Baselines** - Store metrics for regression detection

---

**Last Updated:** 2025-11-08
**Maintained By:** Claude Code Assistant
