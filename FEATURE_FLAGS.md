# Feature Flags Reference

Centralized catalog of feature flags used in the Claude Voice MCP platform. Each entry documents purpose, defaults, environments, and rollout guidance.

---

## `PREFER_STRUCTURED_CHART_COMMANDS`

| Property | Value |
| --- | --- |
| **Category** | Frontend (chart control) |
| **Default** | `false` |
| **Environments** | `VITE_PREFER_STRUCTURED_CHART_COMMANDS` (frontend), `PREFER_STRUCTURED_CHART_COMMANDS` (backend fallback) |
| **Description** | When `true`, the UI will consume structured chart commands (`chart_commands_structured`, `chart_objects`) first and ignore legacy string commands when structured payloads are present. |
| **Usage Notes** | Enable only after verifying structured payloads render correctly. Legacy commands remain available for rollback. |
| **Rollout Strategy** | Flip in tandem with `ENABLE_STRUCTURED_CHART_OBJECTS` during Stage 3 of the Phase 1 rollout. |
| **Rollback** | Set to `false` to restore hybrid processing where legacy commands have priority. |

---

## `ENABLE_STRUCTURED_CHART_OBJECTS`

| Property | Value |
| --- | --- |
| **Category** | Backend + Frontend |
| **Default** | `false` |
| **Environments** | `ENABLE_STRUCTURED_CHART_OBJECTS` (backend), `VITE_ENABLE_STRUCTURED_CHART_OBJECTS` (frontend) |
| **Description** | When `true`, backend responses include `chart_objects` (ChartCommandPayloadV2) and frontend hydration logic prefers the structured object if present. |
| **Usage Notes** | Should be enabled gradually per the rollout plan. Structured payloads are still emitted when `false`, but not consumed first. |
| **Rollout Strategy** | Stage 1 (10%) → Stage 2 (50%) → Stage 3 (structured-first) → Stage 4 (100%). |
| **Rollback** | Disable to revert to legacy-only consumption. Note that backend will continue emitting structured payloads, but clients will ignore them. |

---

## Flag Operations

1. **Configuration Locations**
   - **Frontend**: `.env`, `.env.staging`, `.env.production` using `VITE_*` prefix.
   - **Backend**: Environment variables injected at process start (e.g. via `.env`, deployment config).

2. **Deployment Process**
   - Update environment variables.
   - Redeploy affected services (frontend build + backend workers).
   - Monitor Prometheus metrics (`chart_objects_emitted_total`, validation failures) and Grafana dashboards.

3. **Audit & Change Control**
   - Record every flag change in release notes or #eng-release channel.
   - Include timestamp, actor, target percentage, and observed metrics after change.

4. **Fallback Procedure**
   - Set both flags to `false` for immediate rollback.
   - Purge CDN caches if static payloads cached.
   - Notify support and update incident log.

---

For additional rollout guidance see [`PHASE_1_ROLLOUT_PLAN.md`](./PHASE_1_ROLLOUT_PLAN.md).
