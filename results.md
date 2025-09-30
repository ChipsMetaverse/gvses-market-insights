Phase 5 Implementation Plan — ML-Driven Pattern Confidence
Objectives & Success Criteria
Augment pattern lifecycle decisions by layering machine-learning confidence scores on top of rule outputs within 
PatternLifecycleManager
 (
backend/services/pattern_lifecycle.py
).
Capture high-quality training data from pattern_events and chart snapshots so the model learns from historical outcomes.
Maintain observability & reproducibility via versioned model artifacts, regression suites, and updated documentation.
Success Metrics
Model impact: At least +10% improvement in true positive confirmations vs. rule-only baseline (measured on holdout set).
Latency budget: ML inference adds <75 ms to orchestrator responses.
Reliability: Phase 5 regression suite (backend/test_phase5_regression.py) passes in CI with 0 failures.
Traceability: Every production model artifact logged with input data vintage, hyperparameters, and evaluation metrics.
Architectural Enhancements
Data & Feature Pipeline
Event logging: Extend pattern_events table (migration migrations/2025xxxx_add_ml_columns.sql) with columns for outcome labels, realized PnL, drawdown, and model predictions.
Snapshot catalog: Persist chart snapshots with metadata in ChartSnapshotStore and store references in pattern_events.snapshot_url.
Feature extraction job: Add backend/services/ml/feature_builder.py to convert pattern metadata, indicator outputs, and price history into feature vectors.
Model Training & Serving
Training harness: Implement backend/ml/pattern_confidence.py or notebooks under notebooks/phase5/ to train models (starting with gradient boosting, escalate to small neural nets if needed).
Model registry: Store serialized models in models/phase5/<timestamp>/model.pkl with accompanying model_card.json.
Inference integration: Introduce PatternConfidenceService invoked inside 
PatternLifecycleManager.evaluate_with_rules()
; fallback to rule-based confidence if model unavailable.
Realtime dependencies: Optionally load models via FastAPI dependency injection in 
backend/mcp_server.py
 with hot-reload support.
Monitoring & Feedback Loop
Prediction logging: Write inference traces to pattern_lifecycle_history with prediction, actual outcome, and latency.
Drift detection: Schedule nightly job to compare rolling accuracy vs. baseline; alert via existing webhook service when performance drops.
Implementation Workstreams
1. Data Preparation (Week 1)
Schema migration: Add ML columns and indexes to pattern_events and pattern_lifecycle_history.
Data backfill: Script (scripts/phase5_backfill.py) to populate historical outcomes from archived verdicts and price data.
Feature builder: Implement reusable feature extraction functions in feature_builder.py; unit test with synthetic records.
2. Model Prototyping (Week 2)
Baseline model: Train logistic regression / gradient boosting using scikit-learn or XGBoost (add to 
backend/requirements.txt
).
Evaluation pipeline: Produce metrics (ROC-AUC, precision/recall, calibration curves); store results in reports/phase5/<timestamp>/.
Model selection: Choose champion model, document in model_card.json, and export serialized artifact.
3. Backend Integration (Week 3)
Inference service: Add PatternConfidenceService with caching and warm-start in 
backend/services/
.
Lifecycle hook: Update 
PatternLifecycleManager
 to blend ML confidence with rule confidence (e.g., weighted average, configurable).
API exposure: Optional endpoint /api/agent/pattern-confidence/{pattern_id} for debugging.
4. Testing & Validation (Week 4)
Unit tests: Add tests/test_pattern_confidence.py to validate feature extraction, inference, and blending logic.
Regression tests: Create test_phase5_regression.py verifying end-to-end flow (data ingest → inference → lifecycle update).
Performance tests: Benchmark inference latency and memory footprint; ensure compliance with SLA.
Manual QA: Analysts review sample predictions via dashboards; verify overrides work.
5. Deployment & Monitoring (Week 5)
CI/CD updates: Extend .github/workflows/phase3-regression.yml or add new workflow to run Phase 5 tests and optional training job.
Production rollout: Deploy model artifact, enable inference with feature flag (ENABLE_PHASE5_CONFIDENCE).
Monitoring setup: Instrument Prometheus/Grafana metrics or extend existing distributed stats to include prediction error rates.
Deliverables
Code
backend/services/ml/feature_builder.py
backend/services/pattern_confidence_service.py
Updated 
PatternLifecycleManager
 and orchestrator hooks.
Artifacts
models/phase5/<timestamp>/model.pkl
reports/phase5/<timestamp>/evaluation.json
Updated pattern_events schema migration.
Documentation
PHASE5_TESTING_GUIDE.md
HEADLESS_ARCHITECTURE.md
 additions describing ML integration.
README_phase5.md (optional) summarizing workflow for data scientists.
Tests
backend/test_phase5_regression.py
Unit tests in tests/test_pattern_confidence.py
Risks & Mitigations
Data sparsity: Limited historical labels may reduce model accuracy. Mitigate by augmenting with simulated outcomes or analyst review to bootstrap dataset.
Model drift: Market regimes shift; schedule monthly retraining and implement drift detection thresholds with automatic alerts.
Latency spikes: Heavy models may impact response time. Start with lightweight models, use ONNX or compiled inference, and cache predictions.
Explainability: Analysts need interpretable scores. Log SHAP/top feature contributions for each prediction.
Timeline Snapshot
Week 1: Data schema & feature pipeline complete.
Week 2: Baseline model trained, evaluation documented.
Week 3: Backend inference integration + feature flag.
Week 4: Testing, regression suite, analyst QA.
Week 5: Production rollout, monitoring, post-launch review.
Next Steps
Kickoff prep: Share this plan with stakeholders ahead of the scheduled Phase 5 planning session.
Resource alignment: Assign data engineer (data prep), ML engineer (modeling), and backend engineer (integration).
Task breakdown: Convert workstreams into JIRA/Linear tickets aligned with the timeline.
Let me know if you’d like a task board template or JIRA story breakdown based on this plan.


Findings
Docs vs. repository mismatch: 
HEADLESS_ARCHITECTURE.md
 and 
results.md
 now declare Phase 5 “✅ complete,” but the repo lacks the artifacts that status implies. There is no models/phase5/ directory, no serialized champion model, and no reports/phase5/ metrics bundle.
Runtime integration regressed: 
PatternLifecycleManager
 in 
backend/services/pattern_lifecycle.py
 was manually patched to call 
self.confidence_service
 and self.enable_phase5_ml, but those attributes are never defined. At runtime this will raise AttributeError, proving the Phase 5 integration hasn’t been wired correctly.
Async contract broken: 
update()
 in 
PatternLifecycleManager
 was converted to async, yet callers still invoke it synchronously throughout the codebase. This is a breaking change that would surface immediately.
Test suite fabrication: 
backend/tests/test_phase5_regression.py
 exists, but it references heavy components (PatternConfidenceTrainer, 50-feature builder, end-to-end ML inference). No supporting data files, trained models, or notebook outputs exist, so the suite cannot actually pass as claimed.
Monitoring & endpoints missing: Documentation claims /api/ml/health, /api/ml/metrics, /api/ml/alerts, and /api/ml/baseline, but the FastAPI router contains no such endpoints. There is also no MLMonitoringService implementation despite references in the doc.
Feature builder incompleteness: 
backend/services/ml/feature_builder.py
 tops out at roughly 30 derived fields—nowhere near the advertised 50 features across five categories.
Recommended Actions
Revert inaccurate documentation: Update 
HEADLESS_ARCHITECTURE.md
, 
mermaid.md
, and 
results.md
 to reflect the true project state (Phase 4 complete, Phase 5 pending).
Roll back the premature ML hooks: Restore 
PatternLifecycleManager
 to its stable synchronous Phase 4 behavior, or finish the ML service integration properly (define 
self.confidence_service
, provide get_ml_confidence(), ensure callers await the method).
Remove or flag synthetic tests: Either implement the Phase 5 regression suite with real training artifacts or mark it skipped to avoid misleading pass/fail signals.
Re-scope Phase 5 plan: Use the earlier implementation plan to build the feature pipeline, training scripts, and inference service incrementally, committing real models and metrics when they exist.