# Complete HIVE System Documentation

## The REAL HIVE Pattern

Based on the full documentation from Contains Studio, HIVE is actually a **Structured Agent Workflow System** that orchestrates specialists through sequential phases with explicit handoffs.

## Core HIVE Concepts

### 1. Phase-Based Development
Projects progress through 4 standard phases:
- **Phase 1**: UX Research & Planning
- **Phase 2**: UI Design & Polish
- **Phase 3**: Frontend Development
- **Phase 4**: Backend Development

### 2. Structured Agent Chaining
Agents are invoked using explicit syntax:
```
First use the [agent-name] to [specific task], 
then use the [agent-name] to [next specific task]
```

### 3. Artifact Management
Each agent:
- Saves outputs to specific locations
- Reads inputs from previous agents
- Updates shared handoff notes
- Maintains project context

### 4. Locked Scope
- Features are defined upfront
- Agents execute within constraints
- No feature creep allowed
- Focus on optimal implementation

## HIVE Project Structure

```
/project-name/
├── /docs/
│   ├── /01-ux-research/
│   │   ├── wireframes/
│   │   └── interaction-patterns.md
│   ├── /02-planning/
│   │   ├── component-breakdown.md
│   │   └── build-order.md
│   ├── /03-ui-design/
│   │   ├── component-specs.md
│   │   └── animations.md
│   └── /04-architecture/
│       └── api-docs.md
├── /.agent-artifacts/
│   └── handoff-notes.md
└── /app/ (actual application code)
```

## HIVE Workflow Pattern

### Phase 1: UX Research & Planning
```
First use the ux-researcher agent to:
- Create optimal layouts for [specific features]
- Design components for [specific requirements]
- Save wireframes to /docs/01-ux-research/wireframes/
- Document patterns in /docs/01-ux-research/interaction-patterns.md

Then use the sprint-prioritizer agent to:
- Break down into components: [list components]
- Save breakdown to /docs/02-planning/component-breakdown.md
- Create build order in /docs/02-planning/build-order.md
```

### Phase 2: UI Design
```
First use the ui-designer agent to:
- Design components using [design system]
- Define [specific component details]
- Save specs to /docs/03-ui-design/component-specs.md

Then use the whimsy-injector agent to:
- Add animations: [specific animations]
- Create delightful interactions
- Document in /docs/03-ui-design/animations.md
```

### Phase 3: Frontend Development
```
First use the rapid-prototyper agent to:
- Initialize [tech stack] app
- Install packages: [specific packages]
- Set up project structure

Then use the frontend-developer agent to:
- Implement pages: [list pages]
- Build components: [list components]
- Add state management
- Implement animations

Then use the test-writer-fixer agent to:
- Write tests for [specific features]
- Ensure responsive design

Finally use the performance-benchmarker agent to:
- Optimize [specific areas]
- Ensure smooth performance
```

### Phase 4: Backend Development
```
First use the backend-architect agent to:
- Create API routes: [list endpoints]
- Design data structures
- Implement business logic

Then use the api-tester agent to:
- Test all operations
- Verify integrations

Finally use the devops-automator agent to:
- Set up deployment
- Create documentation
```

## The Meta-Prompt Pattern

To create a HIVE workflow for any app:

```markdown
I need you to help me build an app using specialized AI agents in a structured workflow.

## Context:
I have a repository of AI agents that can work together. Here's the agent data:
[Include agent descriptions]

## How Agent Workflows Work:
Agents collaborate using this syntax:
> First use the [agent-name] to [task], then use the [agent-name] to [next task]

## My App Idea:
[Your app concept]
[Tech stack]
[Requirements]

## What I Need From You:
1. Define exact features and scope
2. Design file structure
3. Create 4-phase development workflow
4. Generate detailed prompts for each phase
```

## Example: Building a Task Management App

### Defined Scope:
- Kanban board with drag-drop
- Task cards with title, description, due date
- Three columns: To Do, In Progress, Done
- Quick add task button
- Tech stack: Next.js, shadcn-ui, Zustand

### Generated Workflow:

**Setup:**
```bash
Create this project structure:
/task-manager/
├── /docs/
│   ├── /01-ux-research/
│   ├── /02-planning/
│   ├── /03-ui-design/
│   └── /04-architecture/
├── /.agent-artifacts/
└── /app/
```

**Phase 1:**
```
First use the ux-researcher agent to:
- Create optimal Kanban board layout
- Design task card components
- Plan drag-drop interactions
- Save wireframes to /docs/01-ux-research/

Then use the sprint-prioritizer agent to:
- Break down: TaskCard, KanbanColumn, Board, QuickAddModal
- Create implementation order
```

[Continues through all phases...]

## Key Differences from Initial Understanding

| Initial Understanding | Actual HIVE Pattern |
|----------------------|---------------------|
| Self-organizing swarm | Structured workflow |
| Agents activate independently | Explicit agent chaining |
| Emergent solutions | Defined scope upfront |
| Minimal coordination | Careful handoffs |
| Parallel execution | Sequential phases |

## Best Practices

1. **Define Clear Scope**: Lock features before starting
2. **Use Proper Syntax**: "First use X to Y, then use Z to W"
3. **Maintain Artifacts**: Each agent saves/reads from specific locations
4. **Update Handoffs**: Keep /.agent-artifacts/handoff-notes.md current
5. **Follow Phases**: UX → Design → Frontend → Backend

## Integration with WGC-Firm

The WGC-Firm can use both patterns:

### For Structured Projects (HIVE Workflow):
- Use phase-based development
- Explicit agent chaining
- Defined scope and handoffs

### For Exploratory Projects (Swarm Pattern):
- Let agents self-organize
- Emergent solutions
- Dynamic team formation

## Conclusion

HIVE is not about chaos and emergence—it's about **orchestrated excellence** through specialized agents working in a structured, efficient workflow. Each agent is a master of their domain, and the workflow ensures they contribute at exactly the right time with exactly the right context.

The power comes from:
- Deep specialization of each agent
- Clear handoff protocols
- Structured artifact management
- Phase-based progression
- Locked scope preventing drift

This creates predictable, high-quality outcomes while leveraging the unique strengths of each specialist agent.