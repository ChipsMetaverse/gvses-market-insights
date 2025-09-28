## Phase 3 Implementation Plan — Headless Chart Service

The Phase 2 multi-worker coordination layer is verified (Supabase schema in place, worker endpoints online). Phase 3 focuses on closing the loop with real-time visualization, operator controls, and observability for distributed workers. The plan below assumes Phase 2 services remain green and outlines the complete work stream from design through launch.

### 1. Objectives
- **Enhance chart delivery UX**: Stream pattern overlays and annotations to the frontend in real time while preserving historical context.
- **Empower human validation**: Provide interactive controls for analysts to accept, reject, or annotate machine-generated patterns.
- **Operationalize multi-worker insights**: Surface worker health, lease activity, and job timelines through dashboards and notifications.
- **Harden distributed reliability**: Expand testing, alerting, and rollback processes to ensure resilience at scale.

### 2. Scope & Deliverables
- **Pattern Streaming Pipeline**
  - Real-time overlay sync via headless WebSocket events.
  - Snapshot delta format (geometry + metadata) for efficient payloads.
  - Backfill API for recent overlays to recover from missed events.
- **Analyst Interaction Layer**
  - Frontend controls (accept/reject/defer) with backend endpoints to persist verdicts.
  - Pattern audit trail (timestamps, decisions, operator notes) visible in UI.
  - Notification hooks (webhook + email/slack adapter) for items requiring review.
- **Worker & Job Observability**
  - `GET /distributed/stats` expansion (lease age, orphan count, per-worker utilization trend).
  - Frontend dashboard widget with inline charts (workers, queues, errors).
  - Alert policy definitions (Supabase function + webhook) for worker heartbeat gaps and orphan bursts.
- **Reliability & Tooling**
  - Lease chaos tests (forced worker failure, random lease expiry) automated in CI.
  - Load test harness hitting `/render` with multi-worker orchestration.
  - Playwright smoke pack validating overlay rendering + analyst actions.

### 3. Work Breakdown Structure

- **3.1 Data & API Layer**
  - Extend `backend/services/agent_orchestrator.py` to emit normalized overlay deltas.
  - Add `POST /agent/pattern-verdict` + `GET /agent/pattern-history` in `backend/routers/agent_router.py`.
  - Update `backend/headless_chart_service/src/server.ts` to broadcast overlay events and store analyst feedback in Supabase (`headless_pattern_verdicts`).
- **3.2 Frontend Enhancements**
  - Upgrade `frontend/src/components/TradingDashboardSimple.tsx` to subscribe to overlay streams, merge delta updates, and render timeline history.
  - Build `PatternReviewPanel` component with decision buttons, notes modal, and history table.
  - Create `WorkerHealthCard` using data from new `/distributed/stats` fields (sparkline via lightweight chart library).
- **3.3 Observability & Alerts**
  - Add Supabase function `notify_worker_alert(worker_id, reason)` triggered by heartbeat delta; integrate with webhook service.
  - Implement `backend/headless_chart_service/src/webhookService.ts` rule set (worker_offline, lease_expired, orphan_recovered).
  - Document runbook updates (`docs/headless/phase3_runbook.md`).
- **3.4 Testing & QA**
  - Unit tests for new orchestrator routes (pytest) and headless queue analytics (node:test).
  - Integration tests: multi-worker scenario with forced failure, verifying lease reassignment and overlay restoration.
  - Load & chaos suite scripted via `scripts/phase3_validations.sh` (k6 + custom Node harness).
- **3.5 Documentation & Enablement**
  - Update `HEADLESS_ARCHITECTURE.md`, `mermaid.md`, and create `results.md` progress log entries.
  - Publish analyst workflow guide (`docs/analyst_review.md`).
  - Conduct training session (recorded Loom) covering new controls and dashboards.

### 4. Timeline (Indicative, 3-Week Sprint)
- **Week 1**: API & data model extensions, Supabase migrations for pattern verdicts, backend overlay events, baseline tests.
- **Week 2**: Frontend pattern review UI, integration with streaming pipeline, worker dashboard, end-to-end manual QA.
- **Week 3**: Observability automation, chaos/load testing, documentation, stakeholder sign-off, production rollout.

### 5. Dependencies & Risks
- Supabase service role credentials must include new tables (`headless_pattern_overlays`, `headless_pattern_verdicts`).
- Playwright/Chromium resource usage will increase with overlay rendering; monitor memory footprint.
- Analyst input requires authentication/authorization updates (ensure tokens include analyst role claims).
- Alert fatigue risk: tune thresholds and support quiet hours.

### 6. Verification & Exit Criteria
- Streaming overlay events visible in dashboard without manual refresh.
- Analyst decisions persisted and reflected across sessions within 2 seconds.
- Worker dashboard shows accurate utilization and alerts on simulated failure.
- Chaos test suite passes (lease expiration, worker crash, network partition).
- Documentation published and training completed.
- Stakeholders sign Phase 3 acceptance checklist.

### 7. Post-Launch Monitoring
- Track key metrics: overlay latency, analyst decision rate, orphan recovery time, worker downtime.
- Schedule weekly review of alert noisiness and adjust thresholds.
- Plan backlog for Phase 4 (pattern intelligence) based on analyst feedback.

> Keep this plan updated as milestones complete. Record status changes and metrics snapshots directly beneath each section to maintain a living artifact.