# Phase 1 – Structured Chart Payload Rollout Plan

## Objective
Deliver the structured chart payload (ChartCommandPayloadV2) to 100% of traffic without user-visible regressions while maintaining the ability to roll back instantly.

## Preconditions
- ✅ Backend emitting both legacy (`chart_commands`) and structured (`chart_commands_structured`, `chart_objects`) payloads.
- ✅ Frontend can parse legacy + structured payloads simultaneously.
- ✅ Feature flags available:
  - `PREFER_STRUCTURED_CHART_COMMANDS`
  - `ENABLE_STRUCTURED_CHART_OBJECTS`

## Stage Plan

| Stage | Flag Settings | Audience | Duration | Success Criteria |
|-------|---------------|----------|----------|------------------|
| 0. Hybrid Baseline | `ENABLE_STRUCTURED_CHART_OBJECTS=false`<br>`PREFER_STRUCTURED_CHART_COMMANDS=false` | 100% | 24h minimum | • No schema validation errors<br>• All dashboards quiet<br>• Capture baseline metrics (latency, error rate, legacy payload usage) |
| 1. Canary | `ENABLE_STRUCTURED_CHART_OBJECTS=true` for 10% of sessions (using hash-based assignment)<br>`PREFER_STRUCTURED_CHART_COMMANDS=false` | 10% | 24h | • Canary cohort error rate ≤ control +0.5%<br>• Validation error rate <0.1%<br>• Support teams notified |
| 2. Ramp | `ENABLE_STRUCTURED_CHART_OBJECTS=true` for 50%<br>`PREFER_STRUCTURED_CHART_COMMANDS=false` | 50% | 24–48h | • Stable metrics vs. Stage 1<br>• Prometheus adoption counter shows ≥40% structured usage |
| 3. Structured First | `ENABLE_STRUCTURED_CHART_OBJECTS=true`<br>`PREFER_STRUCTURED_CHART_COMMANDS=true` for 50% | 50% | 24h | • Chart rendering latency unaffected (<5% variance)<br>• Structured parsing errors <0.1% |
| 4. Full Rollout | Both flags `true` for 100% | 100% | Continuous | • All charts operating in structured mode<br>• Optional: deprecate legacy payload after 2 weeks of stability |

## Rollback Procedures
1. Disable `PREFER_STRUCTURED_CHART_COMMANDS` → re-enable legacy-first consumption.
2. If severe regressions persist, also disable `ENABLE_STRUCTURED_CHART_OBJECTS` → revert to legacy-only payloads.
3. In either rollback, clear CDN caches and notify support channel.
4. Record incident in runbook with metrics snapshots.

## Monitoring & Alerts
- **Metrics**: structured vs. legacy usage, validation failures, chart execution errors.
- **Alerts**:
  - `StructuredValidationErrors > 0.1% (5m)`
  - `ChartRenderFailures > baseline + 1%`
  - `Latency p95 > baseline + 100ms`
- Grafana dashboard: *Phase 1 – Structured Chart Migration* (usage vs. errors).

## Observability Checklist
- [ ] Prometheus counter for `chart_objects_emitted_total`.
- [ ] Prometheus counter for validation failures.
- [ ] Logs tagged with `chart_objects` rollout stage.
- [ ] Support playbook updated.

## Communications
- Announce Stage transitions in #eng-release.
- Notify customer success prior to Stage 3.
- Summarize findings after full rollout.

## Post-Rollout
- Freeze legacy payload changes.
- Plan deprecation timeline for `chart_commands` strings.
- Add automated migration metrics report to weekly ops review.
