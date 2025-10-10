# 9 MCP Servers Implementation Guide

**Source**: "9 MCP Servers That'll Make Vibe Coders Cry Tears Of Joy" - Sean Kochel
**Video ID**: 68e8265aee47cf4224a3f36a
**Analysis Date**: October 9, 2025

---

## Overview

Sean Kochel's video covers 9 production MCP servers he uses regularly in his development workflow. These tools enhance productivity, maintain code quality, and streamline development processes.

---

## The 9 MCP Servers

### 1. **Linear MCP** ⚠️ Not Set Up

**What it does**:
- Tracks issues and manages feature builds
- Adds items to backlog during development
- Integrates with development workflows
- Prioritizes and manages backlogs effectively

**Key Features**:
- Analyze apps for performance bottlenecks
- Recommend optimizations
- Create tickets for issues (database queries, front-end caching)
- Sync work with prioritized backlog
- Prevent chaos by managing critical issues

**Use Cases for G'sves**:
- Track bugs and feature requests
- Manage Agent Builder migration tasks
- Prioritize backend optimizations
- Track performance issues

**Implementation Priority**: ⭐⭐⭐ Medium
- Useful for project management
- Not critical for day-to-day coding

---

### 2. **Perplexity MCP** ⚠️ Not Set Up

**What it does**:
- Research new features and best practices
- Find solutions from other developers
- Bridge gap between possible and optimal
- Provide concrete recommendations

**Key Features**:
- Combine multiple searches
- Research APIs (e.g., Gemini API for image manipulation)
- Find best practices for caching, optimization
- Help with areas where you're not an expert

**Use Cases for G'sves**:
- Research trading algorithms
- Find best practices for voice AI integration
- Explore new financial APIs
- Debug complex backend issues

**Implementation Priority**: ⭐⭐⭐⭐ High
- Extremely useful for research and learning
- Great for exploring new features

---

### 3. **GitHub MCP** ⚠️ Not Set Up

**What it does**:
- Repository management
- Issue creation and tracking
- Pull request automation
- Branch management

**Key Features**:
- Create bug branches automatically
- Generate issues from code analysis
- Automate PR creation
- Track mergers and maintain version control
- Prevent technical debt

**Use Cases for G'sves**:
- Automate issue creation for bugs
- Manage Agent Builder migration PRs
- Track code review process
- Maintain development best practices

**Implementation Priority**: ⭐⭐⭐⭐⭐ Critical
- Essential for team collaboration
- Automates repetitive git tasks

---

### 4. **Supabase MCP** ✅ Already Have (Indirectly)

**What it does**:
- Investigate database table states
- Understand database connectivity
- Diagnose data integrity issues
- Quick database queries without manual SQL

**Key Features**:
- Reference database state easily
- Find relevant tables and entries
- Investigate why data isn't loading
- Ensure app and database sync

**Use Cases for G'sves**:
- Debug conversation persistence issues
- Investigate voice transcript storage
- Check user data integrity
- Troubleshoot Supabase realtime issues

**Implementation Priority**: ⭐⭐ Low (Already integrated)
- We already use Supabase directly in backend
- MCP would add convenience, not functionality

---

### 5. **Context7 (ContextX) MCP** ✅ Already Have

**What it does**:
- Always up-to-date documentation
- Prevent AI hallucinations about APIs
- Provide accurate framework documentation
- Ensure architecture based on current info

**Key Features**:
- Pull relevant documentation on demand
- Prevent using outdated information
- Research multi-agent teams
- Get best practices for implementations

**Use Cases for G'sves**:
- Research React best practices
- Get up-to-date FastAPI documentation
- Learn ElevenLabs API changes
- Explore Agent Builder updates

**Implementation Priority**: ✅ Already Implemented
- We have context7 MCP server configured
- Currently used for documentation retrieval

---

### 6. **Playwright MCP** ⚠️ Not Set Up

**What it does**:
- Automate end-to-end browser tests
- Create self-grading UIs
- Take browser snapshots
- Iteratively improve UI quality

**Key Features**:
- Grade UI against predefined standards
- Send feedback to LLM for fixes
- Automated testing workflows
- Self-checking quality system

**Use Cases for G'sves**:
- Test trading dashboard UI automatically
- Verify voice assistant interface
- Grade chart rendering quality
- Automate E2E testing for frontend

**Implementation Priority**: ⭐⭐⭐⭐ High
- Critical for maintaining UI quality
- Automates tedious manual testing

---

### 7. **Semgrep MCP** ⚠️ Not Set Up

**What it does**:
- Automate security checks in code
- Identify vulnerabilities
- Provide dependency update recommendations
- Ensure codebase security

**Key Features**:
- Run comprehensive security scans
- Find dependency vulnerabilities
- Provide update recommendations
- Prevent obvious security holes

**Use Cases for G'sves**:
- Scan backend for vulnerabilities
- Check frontend dependencies
- Audit API key handling
- Verify Supabase security practices

**Implementation Priority**: ⭐⭐⭐⭐⭐ Critical
- Security is non-negotiable
- Should be run regularly on codebase

---

### 8. **VibeCheck MCP** ⚠️ Not Set Up

**What it does**:
- Metacognitive oversight for AI agents
- Prevent over-engineering
- Provide reflective pauses
- Keep LLMs aligned with project goals

**Key Features**:
- Inject reflective pauses during development
- Prevent reasoning lock-in
- Capture and store mistakes
- Ensure alignment with user intentions

**Use Cases for G'sves**:
- Prevent Agent Builder workflow over-complexity
- Keep voice assistant responses on-track
- Ensure backend APIs don't over-engineer
- Align AI responses with trading education goals

**Implementation Priority**: ⭐⭐⭐ Medium
- Useful for complex AI projects
- Helps prevent scope creep

---

### 9. **Pieces MCP** ⚠️ Not Set Up

**What it does**:
- Configure and monitor multiple apps
- Form memories around development tasks
- Recall past solutions
- Learn from previous mistakes

**Key Features**:
- Watch apps running on machine
- Use information from various screens
- Find memories of past configurations
- Have conversations about solutions/blockers

**Use Cases for G'sves**:
- Remember voice debugging solutions
- Recall backend deployment fixes
- Find past configuration patterns
- Reuse trading algorithm solutions

**Implementation Priority**: ⭐⭐⭐ Medium
- Very useful for complex projects
- Reduces repetitive problem-solving

---

## Implementation Summary

### ✅ Already Have (2/9)
1. Supabase MCP (integrated directly in backend)
2. Context7 MCP (configured and working)

### ⭐⭐⭐⭐⭐ Critical Priority (2/9)
3. **GitHub MCP** - Essential for team collaboration and automation
4. **Semgrep MCP** - Critical for security auditing

### ⭐⭐⭐⭐ High Priority (2/9)
5. **Perplexity MCP** - Excellent for research and learning
6. **Playwright MCP** - Critical for UI quality and testing

### ⭐⭐⭐ Medium Priority (3/9)
7. **Linear MCP** - Useful for project management
8. **VibeCheck MCP** - Helps prevent over-engineering
9. **Pieces MCP** - Reduces repetitive problem-solving

---

## Installation Approach

### Phase 1: Security & Team Essentials ✅ COMPLETED (Oct 9, 2025)
```bash
# 1. Semgrep MCP - Uses Python via uvx (no pre-install needed)
# Package: semgrep-mcp (PyPI)
# Configured to run via uvx on-demand

# 2. GitHub MCP - Already installed ✅
# Package: @modelcontextprotocol/server-github
```

### Phase 2: Development Quality ✅ COMPLETED (Oct 9, 2025)
```bash
# 3. Playwright MCP - Uses npx (no pre-install needed)
# Package: @playwright/mcp@latest
# Official Microsoft implementation

# 4. Perplexity MCP - Uses npx (no pre-install needed)
# Package: @perplexity-ai/mcp-server
# Official Perplexity AI implementation
```

### Phase 3: Workflow Enhancement (Future)
```bash
# 5. Linear MCP
# Package: Remote server at https://mcp.linear.app/sse
# Use: npx -y mcp-remote https://mcp.linear.app/sse

# 6. VibeCheck MCP
# Package: TBD (need to research official package)

# 7. Pieces MCP
# Package: TBD (need to research official package)
```

---

## Claude Desktop Configuration ✅ COMPLETED

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

Successfully added to configuration (Oct 9, 2025):

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": [
        "/usr/local/lib/node_modules/@modelcontextprotocol/server-github/dist/index.js"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "semgrep": {
      "command": "/Users/MarcoPolo/.local/bin/uvx",
      "args": ["semgrep-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "your_key_here"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

**Note**: Linear, VibeCheck, and Pieces are planned for Phase 3 implementation.

---

## Next Steps

1. ✅ Video analyzed and MCP servers identified
2. ✅ Created detailed installation guide for each server
3. ✅ Researched exact npm package names
4. ✅ Installed Phase 1 servers (GitHub ✅ already had, Semgrep ✅)
5. ✅ Installed Phase 2 servers (Playwright ✅, Perplexity ✅)
6. 🔄 **NEXT**: Restart Claude Desktop to activate new MCP servers
7. 🧪 **NEXT**: Test each new server (Semgrep, Playwright, Perplexity)
8. 📊 Evaluate impact on G'sves development workflow
9. 🚀 Plan Phase 3 rollout (Linear, VibeCheck, Pieces)

---

## Installation Summary (Oct 9, 2025)

### ✅ Already Installed
- **GitHub MCP**: @modelcontextprotocol/server-github (pre-existing)
- **Context7 MCP**: @upstash/context7-mcp (pre-existing)
- **Supabase**: Integrated directly in backend (no MCP server needed)

### ✅ Newly Installed (Phase 1 & 2)
- **Semgrep MCP**: semgrep-mcp via uvx (Security scanning)
- **Playwright MCP**: @playwright/mcp@latest via npx (E2E testing)
- **Perplexity MCP**: @perplexity-ai/mcp-server via npx (Research & web search)

### 📝 Not Yet Installed (Phase 3)
- **Linear MCP**: Remote server approach needed
- **VibeCheck MCP**: Package research needed
- **Pieces MCP**: Package research needed

---

## Testing Instructions

After restarting Claude Desktop, test each new server:

### Test Semgrep MCP
```
Ask Claude: "Run a security scan on the backend directory of this project"
Expected: Semgrep will scan code for vulnerabilities
```

### Test Playwright MCP
```
Ask Claude: "Open a browser and navigate to https://gvses-market-insights.fly.dev"
Expected: Playwright will launch browser and take accessibility snapshot
```

### Test Perplexity MCP
```
Ask Claude: "Use Perplexity to research the latest FastAPI best practices for 2025"
Expected: Perplexity will search web and return real-time information
```

---

## Resources

- **Video**: "9 MCP Servers That'll Make Vibe Coders Cry Tears Of Joy" - Sean Kochel
- **TwelveLabs Video ID**: 68e8265aee47cf4224a3f36a
- **Analysis Results**: `/tmp/mcp_analysis_results.txt`
- **Official MCP Docs**: https://docs.anthropic.com/en/docs/build-with-claude/mcp
- **Config Backup**: `~/Library/Application Support/Claude/claude_desktop_config.json.backup_*`

---

**Created**: October 9, 2025
**Last Updated**: October 9, 2025 4:45 PM
**Status**: Phase 1 & 2 Complete - Ready for Testing
**Next Action**: Restart Claude Desktop and test new MCP servers
