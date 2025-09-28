# Phase 4 Testing & Tuning Guide

## Overview
Phase 4 introduces rule-driven pattern lifecycle management across the backend orchestrator, rule engine, and command builders. This guide captures the required steps to validate the release, adjust runtime thresholds, and prove compliance for CI/CD.

## Key Artifacts
- `backend/phase4_regression_output_20250927T225848.txt` – archived console log from the latest green run of `test_phase4_regression.py`.
- `backend/phase4_regression_results.json` – auto-generated summary written by the regression suite.
- `backend/config/pattern_rules.yaml` – authoritative pattern threshold configuration loaded by `PatternRuleEngine` at runtime.

## Regression Test Execution
1. Ensure backend dependencies are installed (`pip install -r backend/requirements.txt`).
2. From the `backend/` directory run:
   ```bash
   python3 test_phase4_regression.py
   ```
3. Expected result: **OK (skipped=7)** with warnings about Supabase credentials if local secrets are omitted.
4. Capture the console output:
   ```bash
   python3 test_phase4_regression.py | tee phase4_regression_output_$(date +%Y%m%dT%H%M%S).txt
   ```
5. Commit the updated `phase4_regression_results.json` and the newly created log file.

## Pattern Rule Tuning
The rule engine now reads thresholds from `backend/config/pattern_rules.yaml`. Adjustments can be made without touching Python code.

### Editing Rules
1. Modify the relevant pattern entry in `pattern_rules.yaml`, e.g.:
   ```yaml
   double_top:
     target_hit_threshold: 0.90
     confidence_decay_rate: 0.03
     max_duration_hours: 48
     invalidation_breach: 1.02
     min_confidence: 0.35
   ```
2. Save the file and rerun the regression suite to validate the new thresholds.
3. Document rationale for changes in the commit message or accompanying changelog.

### Validating Updates
- After editing the YAML, run `python3 test_phase4_regression.py` and confirm all assertions still pass.
- Archive the fresh console output in `backend/` (see commands above).
- Push both the YAML and the log so teammates and CI see the effective configuration.

## CI/CD Notes
- `.github/workflows/phase3-regression.yml` should be extended (or duplicated) to run `python3 test_phase4_regression.py` when Phase 4 gating becomes mandatory.
- If Supabase service keys are required for end-to-end tests, add them as encrypted GitHub Secrets before enabling the Phase 4 suite in CI.

## Troubleshooting
- **Missing YAML**: The rule engine falls back to hard-coded defaults and logs `Pattern rules YAML not found`.
- **Invalid rule schema**: Any parsing failure results in a fallback to defaults; fix the YAML and rerun.
- **Deprecation warnings**: `pattern_lifecycle.py` still uses `datetime.utcnow()` in legacy paths—harmless but marked for cleanup.

## Contact
For questions about pattern thresholds or lifecycle automation, file an issue tagged `phase4-pattern-logic` or reach out to the trading analytics team.
