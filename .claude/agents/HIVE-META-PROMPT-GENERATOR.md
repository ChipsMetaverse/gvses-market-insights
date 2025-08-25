# HIVE Meta-Prompt Generator

## Quick Start Template

Copy and fill in this template to generate a complete HIVE workflow for your app:

```markdown
I need you to help me build an app using specialized AI agents in a structured workflow.

## Context:
I have a repository of AI agents from Contains Studio that work together through structured phases. The agents include: rapid-prototyper, frontend-developer, backend-architect, ui-designer, ux-researcher, sprint-prioritizer, whimsy-injector, test-writer-fixer, api-tester, performance-benchmarker, devops-automator, and 40+ more specialists.

## How Agent Workflows Work:
Agents collaborate using this syntax:
> First use the [agent-name] to [task], then use the [agent-name] to [next task]

## Requirements:
1. Define the EXACT features and scope (no feature creep)
2. Design file structure with /docs/, /.agent-artifacts/, and /app/
3. Create 4-phase workflow: UX → UI → Frontend → Backend
4. Each agent saves outputs and reads from previous agents
5. No web search allowed

## My App Idea:
App Name: [YOUR APP NAME]
Description: [WHAT IT DOES]
Tech Stack: [FRONTEND], [BACKEND], [DATABASE]
Key Features: [LIST 3-5 CORE FEATURES]
Target Users: [WHO WILL USE THIS]
Unique Aspect: [WHAT MAKES IT SPECIAL]

## What I Need From You:
Generate:
1. Exact feature list with detailed scope
2. Complete file structure
3. Initial setup instructions
4. Detailed prompts for all 4 phases with specific agent chains
5. Where each agent saves/reads files

Make it production-ready with polished UI and smooth interactions.
```

## Filled Example: Meditation App

```markdown
I need you to help me build an app using specialized AI agents in a structured workflow.

## Context:
I have a repository of AI agents from Contains Studio that work together through structured phases. The agents include: rapid-prototyper, frontend-developer, backend-architect, ui-designer, ux-researcher, sprint-prioritizer, whimsy-injector, test-writer-fixer, api-tester, performance-benchmarker, devops-automator, and 40+ more specialists.

## How Agent Workflows Work:
Agents collaborate using this syntax:
> First use the [agent-name] to [task], then use the [agent-name] to [next task]

## Requirements:
1. Define the EXACT features and scope (no feature creep)
2. Design file structure with /docs/, /.agent-artifacts/, and /app/
3. Create 4-phase workflow: UX → UI → Frontend → Backend
4. Each agent saves outputs and reads from previous agents
5. No web search allowed

## My App Idea:
App Name: ZenFlow
Description: A meditation app with guided sessions and progress tracking
Tech Stack: Next.js 14, Tailwind CSS, Supabase, Vercel
Key Features: 
- Timer with ambient sounds
- Guided meditation library
- Progress tracking with streaks
- Daily reminders
- Mood check-ins
Target Users: Busy professionals seeking daily mindfulness
Unique Aspect: AI-generated personalized meditation scripts based on mood

## What I Need From You:
Generate:
1. Exact feature list with detailed scope
2. Complete file structure
3. Initial setup instructions
4. Detailed prompts for all 4 phases with specific agent chains
5. Where each agent saves/reads files

Make it production-ready with polished UI and smooth interactions.
```

## Common Tech Stack Templates

### Modern Web App:
```
Tech Stack: Next.js 14, Tailwind CSS, Prisma, PostgreSQL, Vercel
```

### Mobile App:
```
Tech Stack: React Native, Expo, NativeWind, Supabase, EAS Build
```

### Progressive Web App:
```
Tech Stack: Vue 3, Vuetify, IndexedDB, Workbox, Netlify
```

### Real-time App:
```
Tech Stack: SvelteKit, Socket.io, Redis, MongoDB, Railway
```

### AI-Powered App:
```
Tech Stack: Next.js, OpenAI API, Pinecone, Clerk Auth, Vercel
```

## Feature Definition Examples

### Task Management:
```
Key Features:
- Kanban board with drag-and-drop
- Task cards with title, description, due date, assignee
- Custom status columns
- Quick add task with keyboard shortcut
- Filter by assignee, due date, status
```

### Social Platform:
```
Key Features:
- User profiles with avatar and bio
- Post creation with images/text
- Like, comment, share functionality
- Follow/unfollow users
- Personalized feed algorithm
```

### E-Learning:
```
Key Features:
- Course catalog with search/filter
- Video lessons with progress tracking
- Interactive quizzes with instant feedback
- Discussion forums per course
- Completion certificates
```

### Analytics Dashboard:
```
Key Features:
- Real-time data visualization
- Custom date range selection
- Export reports as PDF/CSV
- Scheduled email reports
- Role-based access control
```

## Pro Tips for Better Results

### 1. Be Specific About UI:
Instead of: "User dashboard"
Use: "Dashboard with 4 metric cards showing daily active users, revenue, conversion rate, and churn"

### 2. Define Data Relationships:
Instead of: "User management"
Use: "Users can create teams, invite members via email, assign roles (admin/member/viewer)"

### 3. Specify Interactions:
Instead of: "Interactive charts"
Use: "Charts with hover tooltips, click to drill down, pan/zoom on mobile"

### 4. Include Edge Cases:
Instead of: "File upload"
Use: "File upload with 10MB limit, progress bar, cancel option, retry on failure"

### 5. Mobile Considerations:
Instead of: "Mobile responsive"
Use: "Touch-optimized with swipe gestures, pull-to-refresh, offline support"

## Output Structure You'll Receive

1. **Exact Features** (locked scope)
2. **File Structure**
   ```
   /your-app/
   ├── /docs/
   │   ├── /01-ux-research/
   │   ├── /02-planning/
   │   ├── /03-ui-design/
   │   └── /04-architecture/
   ├── /.agent-artifacts/
   └── /app/
   ```
3. **Phase 1**: UX Research prompts
4. **Phase 2**: UI Design prompts
5. **Phase 3**: Frontend Development prompts
6. **Phase 4**: Backend Development prompts
7. **Launch Instructions**

## Customization Options

### For MVPs:
Add: "Focus on core features only, skip nice-to-haves"

### For Enterprise:
Add: "Include audit logging, SSO, multi-tenancy"

### For Startups:
Add: "Optimize for viral growth, include sharing features"

### For B2B SaaS:
Add: "Include billing integration, usage analytics, admin panel"

## Remember

- HIVE works best with **clear, specific requirements**
- Agents are **specialists** - let them focus on their expertise
- The **workflow is sequential** - each phase builds on the last
- **Handoff notes** are critical for continuity
- **Trust the process** - it's been optimized through thousands of apps

Ready to build? Copy the template, fill in your details, and watch your app come to life through the power of specialized AI agents working in perfect harmony!