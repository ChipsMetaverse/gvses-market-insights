# GitHub Actions Deployment Setup

## Overview
This repository is configured with automatic deployment to Fly.io production whenever code is pushed to the `master` or `main` branch.

## Automatic Deployment Triggers

The deployment workflow automatically runs when:
1. **Push to master/main** - Any commit pushed to these branches
2. **Merged Pull Request** - When a PR is merged into master/main
3. **Manual Trigger** - Via GitHub Actions UI with optional message

## Workflow Features

### 1. Automated Testing (Pre-deployment)
- Runs Python backend tests (if available)
- Runs JavaScript frontend tests (if available)
- Non-blocking: deployment continues even if tests fail

### 2. Production Deployment
- Deploys to Fly.io using remote builders
- Rolling deployment strategy for zero downtime
- Automatic health checks after deployment
- Smoke tests for critical endpoints

### 3. Deployment Verification
- Health endpoint verification (6 attempts, 10s apart)
- Stock price endpoint test
- Agent orchestrator endpoint test
- Deployment summary generation

## Setup Instructions

### Step 1: Add Fly.io API Token to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name**: `FLY_API_TOKEN`
   - **Value**: Your Fly.io deploy token (see below)

### Step 2: Get Your Fly.io Deploy Token

Option 1: Use the token already generated:
```
FlyV1 fm2_lJPECAAAAAAACT/jxBBq26uWKAMqNp9LRxTyCJcIwrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABGjiB8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDxowu25il11te9cJ5o1zp7s3ue9PTjW6XyClra0xsXJQbJtsw5ioVLqVSnfPoGRwBdwyYgDODP/9AjP0tDETous+NbaU5rpbiONGI9FVEZCEA5ZMtFwxS+LjMB8RTu+Roh0K26osODEw1wNtMVlBs5EPyTk8xwh69m1D8HoIxztKYS7KmnKi0mPhMW+MA2SlAORgc4AkM+gHwWRgqdidWlsZGVyH6J3Zx8BxCA9TtGJtjOhSH/HOt+w1bjpDCDwv1q6InCehjddAvn4dw==,fm2_lJPETous+NbaU5rpbiONGI9FVEZCEA5ZMtFwxS+LjMB8RTu+Roh0K26osODEw1wNtMVlBs5EPyTk8xwh69m1D8HoIxztKYS7KmnKi0mPhMW+MMQQLGB0opaNo0COZ3P4GUekLMO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5o2hW0zo5yG9IXzgAQ89YKkc4AEPPWDMQQzDk7C1vwk9BDo/eA5V6UC8Qg33l1RdB2vPfVX0hsYVQFBsdvGBSiVg0tz1Vpz0HyigM=
```

Option 2: Generate a new token:
```bash
fly tokens create deploy
```

### Step 3: Verify Configuration

1. Check that `.github/workflows/deploy.yml` exists
2. Ensure your Fly app name matches: `gvses-market-insights`
3. Verify the branch name in the workflow matches your default branch

## Deployment Process

### What Happens on Each Push

1. **GitHub Actions triggers** the workflow
2. **Tests run** (if configured)
3. **Docker image builds** on Fly.io builders
4. **Rolling deployment** updates machines one by one
5. **Health checks** verify the app is running
6. **Smoke tests** check critical endpoints
7. **Summary generated** with deployment details

### Monitoring Deployments

#### GitHub Actions UI
1. Go to **Actions** tab in your repository
2. Click on the running workflow
3. View real-time logs and status

#### Fly.io Dashboard
- Monitor: https://fly.io/apps/gvses-market-insights/monitoring
- Metrics: https://fly.io/apps/gvses-market-insights/metrics

#### Command Line
```bash
# Check deployment status
fly status --app gvses-market-insights

# View deployment logs
fly logs --app gvses-market-insights

# List recent releases
fly releases --app gvses-market-insights
```

## Manual Deployment

You can trigger a deployment manually:

1. Go to **Actions** tab
2. Select **Deploy to Fly.io Production**
3. Click **Run workflow**
4. Optionally add a deployment message
5. Click **Run workflow** button

## Rollback Procedure

If a deployment fails or causes issues:

```bash
# List releases to find the previous version
fly releases --app gvses-market-insights

# Rollback to a specific version
fly deploy --app gvses-market-insights --image registry.fly.io/gvses-market-insights:deployment-[ID]
```

## Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs for errors
2. Verify Fly.io token is valid
3. Check Dockerfile builds locally
4. Review Fly.io logs: `fly logs --app gvses-market-insights`

### App Unhealthy After Deployment
1. Check health endpoint: https://gvses-market-insights.fly.dev/health
2. View live logs: `fly logs --app gvses-market-insights -f`
3. SSH into machine: `fly ssh console --app gvses-market-insights`
4. Rollback if needed (see above)

### Token Issues
- Tokens expire after 20 years by default
- Regenerate if compromised: `fly tokens create deploy`
- Update GitHub secret with new token

## Security Notes

- **Never commit** the Fly.io token to the repository
- Use GitHub Secrets for all sensitive data
- Tokens are scoped to deployment only
- Rotate tokens periodically for security

## Support

- Fly.io Status: https://status.fly.io
- Fly.io Community: https://community.fly.io
- GitHub Actions Docs: https://docs.github.com/actions

## Current Configuration

- **App Name**: gvses-market-insights
- **Production URL**: https://gvses-market-insights.fly.dev
- **Deploy Branches**: master, main
- **Strategy**: Rolling deployment
- **Health Check**: /health endpoint
- **Timeout**: 30 minutes maximum