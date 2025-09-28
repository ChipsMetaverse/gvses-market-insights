# Phase 3 CI/CD Monitoring Guide

## Initial CI Setup Verification

### GitHub Actions Monitoring
**Repository**: `https://github.com/[your-org]/claude-voice-mcp`  
**Workflow**: `.github/workflows/phase3-regression.yml`

### First Run Checklist

#### 1. Workflow Triggers
- [ ] Push to main branch triggers workflow
- [ ] Push to develop branch triggers workflow  
- [ ] Pull request creation triggers workflow
- [ ] Manual dispatch button available
- [ ] Nightly cron (2 AM UTC) scheduled

#### 2. Workflow Execution
Navigate to: **Actions** → **Phase 3 Regression Tests**

For each run, verify:
- [ ] Pre-flight checks pass (services start correctly)
- [ ] Python dependencies install successfully
- [ ] Node dependencies install successfully
- [ ] Playwright browsers install
- [ ] Backend service starts on port 8000
- [ ] Headless service starts on port 3100
- [ ] Regression tests execute
- [ ] Test results uploaded to artifacts

#### 3. Artifacts Verification
Click on completed workflow run → **Artifacts** section

Expected artifacts:
- `regression-test-results/`
  - `phase3_regression_results.json`
  - Any `*.log` files if errors occurred

Sample `phase3_regression_results.json`:
```json
{
  "timestamp": "2025-09-28T00:00:00Z",
  "total_tests": 3,
  "passed": 3,
  "failed": 0,
  "success_rate": 100.0,
  "execution_time": 0.6,
  "results": [
    {
      "test": "Pattern verdict submission",
      "passed": true,
      "timestamp": "..."
    },
    {
      "test": "Pattern history persistence",
      "passed": true,
      "timestamp": "..."
    },
    {
      "test": "Enhanced distributed stats",
      "passed": true,
      "timestamp": "..."
    }
  ]
}
```

#### 4. Notification Testing

##### Slack Integration (if configured)
- [ ] Success runs: No notification (expected)
- [ ] Failed runs: Slack message sent to configured channel
- [ ] Message includes: Job status, failure reason, workflow link

##### GitHub Issue Creation (on failure)
- [ ] Issue auto-created with title: "Phase 3 Regression Test Failure"
- [ ] Issue labeled: `bug`, `regression`, `phase3`
- [ ] Issue body includes:
  - Branch name
  - Commit SHA
  - Direct link to failed workflow run

### Simulated Failure Test

To verify failure handling, temporarily modify the test:

1. **Create a test branch**:
```bash
git checkout -b test/ci-failure-simulation
```

2. **Modify test to fail**:
```python
# In backend/test_phase3_regression.py, add:
assert False, "Simulated failure for CI testing"
```

3. **Push and observe**:
```bash
git add -A
git commit -m "test: Simulate CI failure"
git push origin test/ci-failure-simulation
```

4. **Verify failure handling**:
- [ ] Workflow shows as failed
- [ ] Slack notification sent (if configured)
- [ ] GitHub issue created
- [ ] Artifacts include failure logs

5. **Clean up**:
```bash
git checkout main
git branch -D test/ci-failure-simulation
```

## Periodic Review Schedule

### Bi-Weekly Review Tasks

Set calendar reminders for every 2 weeks to perform:

#### Week 1 & 3 Reviews (Quick Check)
- [ ] Run local regression tests: `./run_phase3_regression.sh`
- [ ] Check GitHub Actions history for any failures
- [ ] Verify services are healthy
- [ ] Review any open Phase 3 issues

#### Week 2 & 4 Reviews (Deep Check)
- [ ] Complete Week 1 & 3 tasks
- [ ] Update verification evidence document
- [ ] Review CI workflow performance metrics
- [ ] Check for dependency updates
- [ ] Audit test coverage

### Monthly Metrics to Track

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Test Success Rate | > 95% | _____% | ⚪ |
| Average Execution Time | < 2s | _____s | ⚪ |
| CI Pipeline Success Rate | > 90% | _____% | ⚪ |
| Regression Issues Found | 0 | _____ | ⚪ |
| Test Coverage | > 80% | _____% | ⚪ |

## CI/CD Performance Monitoring

### Workflow Performance Baseline

Expected execution times:
- Setup: 30-60 seconds
- Dependency installation: 60-120 seconds
- Service startup: 10-20 seconds
- Test execution: 1-3 seconds
- Artifact upload: 5-10 seconds
- **Total workflow**: 2-4 minutes

### Performance Degradation Alerts

Monitor for:
- [ ] Workflow time > 5 minutes
- [ ] Test execution > 5 seconds
- [ ] Repeated transient failures
- [ ] Service startup failures

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Services Won't Start in CI
**Symptom**: Health check fails
**Solution**: 
- Check environment variables in workflow
- Verify port availability
- Increase startup wait time

#### 2. Playwright Installation Fails
**Symptom**: Browser download errors
**Solution**:
- Clear GitHub Actions cache
- Update Playwright version
- Check runner disk space

#### 3. Regression Tests Timeout
**Symptom**: Tests exceed 20s timeout
**Solution**:
- Check for network issues
- Verify database connections
- Review test data volume

#### 4. Artifacts Not Uploading
**Symptom**: No artifacts after workflow
**Solution**:
- Check file paths in workflow
- Verify artifact size < 500MB
- Review upload action version

## Documentation Updates

### When to Update Evidence

Update `PHASE3_VERIFICATION_EVIDENCE.md` when:
- [ ] New test failures discovered
- [ ] Performance metrics change significantly
- [ ] New features added to Phase 3
- [ ] Risk assessment changes
- [ ] Deployment status changes

### Update Command
```bash
# Append new test results
echo "## Update $(date +%Y-%m-%d)" >> PHASE3_VERIFICATION_EVIDENCE.md
echo "Latest test results:" >> PHASE3_VERIFICATION_EVIDENCE.md
cat backend/phase3_regression_results.json >> PHASE3_VERIFICATION_EVIDENCE.md
```

## Action Items Log

### Immediate Actions
- [ ] Verify GitHub Actions workflow is enabled
- [ ] Test manual workflow dispatch
- [ ] Configure Slack webhook (if using)
- [ ] Set up monitoring dashboard

### First CI Run
- [ ] Monitor live execution
- [ ] Download and verify artifacts
- [ ] Check all notifications work
- [ ] Document any issues

### Ongoing Maintenance
- [ ] Weekly: Check CI history
- [ ] Bi-weekly: Run regression tests
- [ ] Monthly: Update metrics
- [ ] Quarterly: Review test coverage

## Contact Information

| Role | Contact | Responsibility |
|------|---------|----------------|
| DevOps Lead | [Name] | CI/CD pipeline maintenance |
| QA Lead | [Name] | Test suite updates |
| Backend Lead | [Name] | Service health |
| Project Manager | [Name] | Schedule reviews |

---

*Last Updated: September 28, 2025*  
*Next Review: [Set date 2 weeks from now]*