# Vibe Coding Workflow - Autonomous Development System

## 🎯 Core Philosophy
Transform Claude from reactive assistant to proactive development partner using all 12 MCP servers orchestrated together.

## 🔄 Automatic Workflow Triggers

### 1. When You Mention a Bug
```
TRIGGER: "bug", "error", "broken", "not working"
ACTION:
1. Create Linear issue automatically
2. Use Semgrep to scan for related security issues
3. Search GitHub for similar issues
4. Research solution with Perplexity
5. Implement fix
6. Generate tests with Playwright
7. Create GitHub PR
```

### 2. When You Request a Feature
```
TRIGGER: "add", "implement", "create feature", "build"
ACTION:
1. Create Linear issue with feature specs
2. Use Context7 to get latest framework docs
3. Research best practices with Perplexity
4. Design implementation plan
5. Write code
6. Generate tests
7. Security scan with Semgrep
8. Create PR
```

### 3. When You Ask Questions
```
TRIGGER: "how to", "what is", "explain"
ACTION:
1. Check Memory servers for previous answers
2. Search Context7 for documentation
3. Use Perplexity for current information
4. Store answer in Memory for future
```

### 4. When Code is Written
```
TRIGGER: After any code creation/modification
ACTION:
1. Run Semgrep security scan
2. Generate Playwright tests
3. Check GitHub for conflicts
4. Update Linear issue status
5. Store patterns in Memory
```

## 📋 MCP Server Orchestration

### Linear (Project Management)
- **Proactive Uses**:
  - Auto-create issues from conversations
  - Update status as work progresses
  - Generate daily/weekly summaries
  - Track blockers and dependencies

### GitHub (Version Control)
- **Proactive Uses**:
  - Check for conflicts before coding
  - Auto-commit with semantic messages
  - Create PRs with full context
  - Link commits to Linear issues

### Perplexity (Research)
- **Proactive Uses**:
  - Verify best practices before coding
  - Check for security advisories
  - Research performance optimizations
  - Find trending solutions

### Context7 (Documentation)
- **Proactive Uses**:
  - Get docs BEFORE using any library
  - Verify API changes
  - Check deprecation warnings
  - Find migration guides

### Semgrep (Security)
- **Proactive Uses**:
  - Scan EVERY code change
  - Check dependencies for vulnerabilities
  - Validate authentication patterns
  - Audit data handling

### Playwright (Testing)
- **Proactive Uses**:
  - Generate tests for EVERY new component
  - Create E2E tests for features
  - Build regression test suites
  - Test accessibility automatically

### Memory Servers (Knowledge)
- **Proactive Uses**:
  - Remember all solutions
  - Track what didn't work
  - Build pattern library
  - Create knowledge base

## 🚀 Workflow Implementation

### Phase 1: Task Initiation
```python
# When any request comes in:
1. Analyze intent
2. Check Memory for similar tasks
3. Create Linear issue
4. Set up tracking
```

### Phase 2: Research & Planning
```python
# Before coding:
1. Perplexity: Research current best practices
2. Context7: Get latest documentation
3. GitHub: Check existing code patterns
4. Memory: Recall previous solutions
```

### Phase 3: Implementation
```python
# During coding:
1. Write code with real-time doc checking
2. Semgrep: Continuous security scanning
3. Generate tests in parallel
4. Update Linear status to "In Progress"
```

### Phase 4: Quality Assurance
```python
# After coding:
1. Semgrep: Final security audit
2. Playwright: Run generated tests
3. Check code coverage
4. Validate against requirements
```

### Phase 5: Delivery
```python
# Completion:
1. GitHub: Create PR with full context
2. Linear: Update issue with results
3. Memory: Store solution patterns
4. Generate documentation
```

## 🎮 Activation Commands

### Full Autonomous Mode
"Use Vibe Coding workflow for [task]"

### Specific Workflows
- "Track this in Linear"
- "Research best approach"
- "Scan for security issues"
- "Generate comprehensive tests"
- "Remember this solution"

## 🔧 Configuration Rules

### Always Active
- Semgrep after code changes
- Memory for repeated questions
- Context7 before using libraries

### Context-Triggered
- Linear for multi-step tasks
- Perplexity for "best practices"
- Playwright for UI components
- GitHub for collaboration

### User-Requested
- Full workflow execution
- Specific server usage
- Custom automation

## 📊 Success Metrics

### Efficiency Gains
- 80% reduction in manual task tracking
- 100% code security scanning
- 90% test coverage automation
- 70% documentation generation

### Quality Improvements
- Zero security vulnerabilities shipped
- All code has tests
- Every change is tracked
- Knowledge is preserved

## 🎯 Example Workflow Execution

```markdown
User: "Add user authentication to the app"

Claude (Vibe Coding Mode):
1. ✅ Creating Linear issue: "Implement user authentication"
2. 🔍 Researching with Perplexity: "Best authentication practices 2025"
3. 📚 Getting docs from Context7: FastAPI authentication, JWT tokens
4. 💡 Found similar in Memory: Previous OAuth implementation
5. 🔨 Implementing solution...
6. 🔒 Semgrep scan: No vulnerabilities found
7. 🧪 Generated 12 Playwright tests
8. 📦 Creating GitHub PR #45: "feat: Add JWT authentication"
9. ✅ Linear issue updated: Completed
10. 💾 Stored in Memory: Authentication pattern v2
```

## 🚦 Getting Started

1. **Activate Vibe Coding Mode**:
   ```
   "Enable Vibe Coding workflow"
   ```

2. **Set Default Behavior**:
   ```
   "Always use Vibe Coding for development tasks"
   ```

3. **Configure Preferences**:
   ```
   "Set Linear as default tracker"
   "Always scan with Semgrep"
   "Auto-generate Playwright tests"
   ```

## 🔄 Continuous Improvement

The workflow learns and improves:
- Memory servers track what works
- Failed approaches are remembered
- Patterns evolve based on success
- Workflow optimizes over time

---

**Status**: Ready to Activate
**Servers**: All 12 Connected
**Mode**: Awaiting Activation Command