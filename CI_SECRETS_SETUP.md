# GitHub Actions Secrets Setup

To run the complete CI/CD pipeline with all tests, configure these secrets in your GitHub repository settings:

## Required Secrets

Go to **Settings → Secrets and variables → Actions** in your GitHub repository and add:

### Core Secrets
- `SUPABASE_URL`: Your Supabase project URL (e.g., `https://cwnzgvrylvxfhwhsqelc.supabase.co`)
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key (not the anon key)
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude
- `OPENAI_API_KEY`: Your OpenAI API key for GPT services
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `ELEVENLABS_AGENT_ID`: Your ElevenLabs agent ID
- `ALPACA_API_KEY`: Your Alpaca Markets API key
- `ALPACA_SECRET_KEY`: Your Alpaca Markets secret key

### Optional Secrets
- `SLACK_WEBHOOK`: Slack webhook URL for notifications (optional)

## Current Configuration Status

The CI workflow is configured to:
1. **Skip** the headless chart service if Supabase secrets aren't configured
2. **Continue** running backend tests even without all secrets
3. **Use fallback values** for non-critical services

## Setting Up Secrets

1. Navigate to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with its name and value
5. Save each secret

## Security Notes

- Never commit `.env` files to the repository
- Use GitHub secrets for all sensitive information
- Rotate keys regularly
- Use separate keys for production and development

## Testing Without Secrets

The regression tests can still run basic functionality tests without all secrets configured. The workflow will:
- Skip services that require missing secrets
- Log warnings about skipped services
- Continue with available tests

To see which services were skipped, check the GitHub Actions logs.