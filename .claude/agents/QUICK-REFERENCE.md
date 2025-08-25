# Agent System Quick Reference

## 🚀 Quick Start

### Building a Specific App? Use HIVE
```markdown
Copy the meta-prompt from HIVE-META-PROMPT-GENERATOR.md
Fill in: App name, description, tech stack, features
Submit to Claude
Follow the generated 4-phase workflow
```

### Building a Complex System? Use WGC-Firm
```bash
# Strategic planning
Task(subagent_type="wgc-firm-ceo", prompt="[your vision]")

# Technical architecture  
Task(subagent_type="wgc-firm-cto", prompt="[technical needs]")

# Execution
Task(subagent_type="wgc-firm-orchestrator", prompt="[build plan]")
```

## 📊 Decision Matrix

| Need | Use | Command |
|------|-----|---------|
| Build TODO app | HIVE | Meta-prompt → 4 phases |
| Scale to 1M users | WGC-Firm | `wgc-firm-orchestrator` |
| Add payment system | HIVE | `blockchain-payment-specialist` |
| Pivot strategy | WGC-Firm | `wgc-firm-ceo` |
| Polish UI | HIVE | `whimsy-injector` |
| Refactor codebase | WGC-Firm | `senior-engineer` |

## 🎯 Pattern Comparison

### HIVE Workflow
```
Define Features → Phase 1: UX → Phase 2: UI → Phase 3: Frontend → Phase 4: Backend
```
- ✅ Fast (6-day sprints)
- ✅ Predictable outcomes
- ✅ Polished results
- ❌ Fixed scope only

### WGC-Firm Pattern
```
Strategy → Architecture → Parallel Teams → Continuous Evolution
```
- ✅ Handles complexity
- ✅ Strategic thinking
- ✅ Scalable approach
- ❌ Slower initial progress

## 🛠️ Common Workflows

### MVP in a Week
```
1. Use HIVE meta-prompt
2. Define 3-5 core features
3. Execute 4 phases
4. Ship on day 6
```

### Enterprise System
```
1. wgc-firm-ceo: Market analysis
2. wgc-firm-cto: Architecture design
3. wgc-firm-orchestrator: Team assembly
4. Use HIVE for specific modules
```

### Add Feature to Existing App
```
1. local-file-researcher: Understand code
2. Use HIVE Phase 1-4 for new feature
3. code-quality-guardian: Review changes
```

## 🤖 Key Agents

### Always Available (Proactive)
- `code-quality-guardian` - Auto-reviews code
- `whimsy-injector` - Auto-polishes UI
- `test-writer-fixer` - Auto-writes tests

### Leadership (WGC-Firm)
- `wgc-firm-ceo` - Strategy
- `wgc-firm-cto` - Architecture
- `wgc-firm-orchestrator` - Coordination

### Builders (HIVE)
- `rapid-prototyper` - Quick starts
- `frontend-developer` - UI code
- `backend-architect` - APIs
- `mobile-app-builder` - Native apps

### Specialists
- `blockchain-payment-specialist` - Crypto
- `ai-engineer` - ML features
- `growth-hacker` - Viral growth
- `devops-automator` - Deployment

## 💡 Pro Tips

1. **Start Simple**: Use HIVE for MVPs, add WGC-Firm for scale
2. **Mix Patterns**: WGC strategy + HIVE execution = Best results
3. **Trust Agents**: They're experts in their domains
4. **Maintain Handoffs**: Always update `.agent-artifacts/handoff-notes.md`
5. **Lock Scope**: Define features before starting HIVE workflow

## 🎮 Try It Now

### Quick App (HIVE):
```
"Build a habit tracker with Next.js and Supabase"
→ Copy meta-prompt → Get complete workflow
```

### Complex System (WGC-Firm):
```
Task(subagent_type="wgc-firm-orchestrator",
     prompt="Build a multi-tenant SaaS platform")
```

### Just Code Something:
```
Task(subagent_type="rapid-prototyper",
     prompt="Create a fun weekend project")
```

---

**Remember**: You have 40+ expert agents ready to help. Whether you need Silicon Valley strategy or Contains Studio speed, the right pattern is just a command away!