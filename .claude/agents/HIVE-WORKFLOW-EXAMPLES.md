# HIVE Workflow Examples

## Example 1: E-Commerce Mobile App

### App Idea:
"Build a mobile e-commerce app for handmade crafts with React Native and Supabase"

### Generated HIVE Workflow:

#### Defined Features:
1. Product browsing with categories
2. Shopping cart with quantity management
3. User authentication (email/password)
4. Order placement and history
5. Favorite products

#### Project Structure:
```
/craft-commerce/
├── /docs/
│   ├── /01-ux-research/
│   ├── /02-planning/
│   ├── /03-ui-design/
│   └── /04-architecture/
├── /.agent-artifacts/
└── /app/ (React Native app)
```

#### Phase 1 Prompt:
```
Create the project structure above.

First use the ux-researcher agent to:
- Create mobile-first layouts for product grid and detail views
- Design shopping cart flow with easy quantity adjustments
- Plan authentication screens (login, register, profile)
- Optimize checkout process for mobile
- Save wireframes to /craft-commerce/docs/01-ux-research/wireframes/
- Document touch gestures in /craft-commerce/docs/01-ux-research/interaction-patterns.md

Then use the sprint-prioritizer agent to:
- Break down into: ProductCard, ProductGrid, CartItem, CartSummary, AuthForm, OrderCard
- Define navigation structure
- Save to /craft-commerce/docs/02-planning/component-breakdown.md
- Create build priority: Auth → Products → Cart → Orders
- Save to /craft-commerce/docs/02-planning/build-order.md

Update /.agent-artifacts/handoff-notes.md with mobile UX decisions.
```

#### Phase 2 Prompt:
```
First use the ui-designer agent to:
- Design components using React Native Elements
- ProductCard: Image, title, price, favorite button
- CartItem: Image thumbnail, quantity controls, remove button
- Use warm colors for handmade craft aesthetic
- Save specs to /craft-commerce/docs/03-ui-design/component-specs.md

Then use the whimsy-injector agent to:
- Add to cart: Item flies to cart icon animation
- Favorite toggle: Heart fill animation
- Pull-to-refresh: Craft tools spinner
- Empty cart: Friendly illustration
- Document in /craft-commerce/docs/03-ui-design/animations.md

Update /.agent-artifacts/handoff-notes.md with design system.
```

#### Phase 3 Prompt:
```
First use the rapid-prototyper agent to:
- Initialize React Native app with Expo in /craft-commerce/app/
- Install: react-navigation, react-native-elements, react-query, zustand
- Set up Supabase client
- Configure navigation structure

Then use the mobile-app-builder agent to:
- Implement screens:
  * HomeScreen: Product grid with categories
  * ProductDetailScreen: Images, description, add to cart
  * CartScreen: Items list, total, checkout button
  * AuthScreen: Login/register forms
  * ProfileScreen: Orders, favorites, logout
- Add gesture handlers for swipe actions
- Implement offline support with react-query

Then use the test-writer-fixer agent to:
- Test cart calculations
- Test auth flow
- Verify offline functionality

Update /.agent-artifacts/handoff-notes.md with implementation notes.
```

#### Phase 4 Prompt:
```
First use the backend-architect agent to:
- Set up Supabase tables: products, users, orders, cart_items, favorites
- Create RLS policies for user data
- Set up auth with email confirmation
- Create Edge Functions for order processing

Then use the api-tester agent to:
- Test CRUD operations
- Verify RLS policies work correctly
- Test order creation flow

Finally use the devops-automator agent to:
- Set up Expo EAS Build
- Configure environment variables
- Create build process for iOS/Android
- Document in /craft-commerce/docs/04-architecture/deployment.md
```

---

## Example 2: AI Writing Assistant

### App Idea:
"Build an AI writing assistant with Next.js, OpenAI API, and Vercel KV for saving drafts"

### Generated HIVE Workflow:

#### Defined Features:
1. Text editor with AI suggestions
2. Multiple writing modes (blog, email, creative)
3. Draft saving and history
4. AI-powered grammar checking
5. Export to various formats

#### Phase 1 Prompt:
```
Create project structure:
/ai-writer/
├── /docs/
├── /.agent-artifacts/
└── /app/

First use the ux-researcher agent to:
- Design split-screen layout: editor + AI suggestions
- Create mode selector UI
- Plan draft management sidebar
- Design export options menu
- Save to /ai-writer/docs/01-ux-research/

Then use the sprint-prioritizer agent to:
- Components: Editor, SuggestionPanel, ModeSelector, DraftList, ExportMenu
- Build order: Editor → AI Integration → Drafts → Export
- Save to /ai-writer/docs/02-planning/
```

[Continue with remaining phases...]

---

## Example 3: Fitness Tracking PWA

### App Idea:
"Build a fitness tracking PWA with Vue 3, Chart.js, and IndexedDB for offline support"

### Generated HIVE Workflow:

#### Defined Features:
1. Workout logging with exercise library
2. Progress charts and statistics
3. Goal setting and tracking
4. Offline-first with sync
5. PWA installation

[Complete workflow follows same pattern...]

---

## Quick Templates

### SaaS Dashboard Template:
```
First use the ux-researcher agent to:
- Design dashboard layout with key metrics
- Create data visualization components
- Plan filtering and date range selection

Then use the sprint-prioritizer agent to:
- Break down: MetricCard, Chart, DataTable, FilterBar
- Define API requirements
```

### Social Media App Template:
```
First use the ux-researcher agent to:
- Design feed with infinite scroll
- Create post creation flow
- Plan engagement features (like, comment, share)

Then use the sprint-prioritizer agent to:
- Components: PostCard, CreatePost, CommentThread, UserProfile
- Define real-time features
```

### Game Companion App Template:
```
First use the ux-researcher agent to:
- Design character/inventory management
- Create quest tracking interface
- Plan social features (guilds, chat)

Then use the sprint-prioritizer agent to:
- Break down: CharacterCard, InventoryGrid, QuestList, GuildChat
- Define data sync strategy
```

## Tips for Success

1. **Be Specific**: The more detailed your app idea, the better the workflow
2. **Lock Scope**: Define all features upfront to prevent drift
3. **Trust the Process**: Let each agent complete their phase fully
4. **Maintain Handoffs**: Always update handoff-notes.md
5. **Follow Order**: Phases build on each other - don't skip

## Common Patterns

### For CRUD Apps:
- Phase 1: Focus on data display and forms
- Phase 2: Polish with loading states and confirmations
- Phase 3: Implement with proper state management
- Phase 4: Add validation and error handling

### For Real-time Apps:
- Phase 1: Design presence indicators and live updates
- Phase 2: Add connection status UI
- Phase 3: Implement WebSocket handling
- Phase 4: Add message queuing and retry logic

### For Data Visualization:
- Phase 1: Choose appropriate chart types
- Phase 2: Design interactive tooltips
- Phase 3: Implement with performance in mind
- Phase 4: Add data export capabilities

## Troubleshooting

**Issue**: Agents adding features not in scope
**Solution**: Be more explicit in initial scope definition

**Issue**: Handoffs not working smoothly
**Solution**: Ensure each agent explicitly saves to correct location

**Issue**: Phases taking too long
**Solution**: Break down into smaller sub-phases

**Issue**: Quality not meeting expectations
**Solution**: Add specific quality requirements to each phase

Remember: HIVE is about **structured excellence**, not chaotic creativity. The magic happens when specialized agents work in harmony through well-defined phases.