# G'sves Market Insights - Deployment Guide

## 🚀 Quick Start (Local Development)

Run everything with one command:
```bash
./start-dev.sh
```

This will start:
- Backend API (http://localhost:8000)
- Frontend App (http://localhost:5173)
- Public tunnel for webhooks (https://gvses-backend.loca.lt)

## 🐳 Docker Development

```bash
# Create .env file in root with all variables
cp .env.example .env

# Run with Docker Compose
docker-compose up --build
```

## ☁️ Production Deployment

### Option 1: Deploy to Fly.io (Recommended)

Fly.io provides a permanent URL and free tier for small apps.

#### Setup
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly
fly auth login

# Create app
fly apps create gvses-market-insights
```

#### Set Secrets
```bash
fly secrets set ANTHROPIC_API_KEY="your-key"
fly secrets set SUPABASE_URL="your-url"
fly secrets set SUPABASE_ANON_KEY="your-key"
fly secrets set ELEVENLABS_API_KEY="your-key"
fly secrets set ELEVENLABS_AGENT_ID="your-agent-id"
```

#### Deploy
```bash
# Deploy backend
fly deploy

# Your app will be available at:
# https://gvses-market-insights.fly.dev
```

#### Update ElevenLabs Tool
After deployment, update your ElevenLabs tool URL to:
```
https://gvses-market-insights.fly.dev/api/stock-price
```

### Option 2: Deploy to Railway

Railway provides easy deployment with GitHub integration.

1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Create new project from GitHub repo
4. Add environment variables
5. Deploy

### Option 3: Deploy to Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: gvses-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: ELEVENLABS_API_KEY
        sync: false
      - key: ELEVENLABS_AGENT_ID
        sync: false
```

2. Deploy via Render dashboard

## 🔧 Environment Variables

### Backend (.env)
```env
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://...supabase.co
SUPABASE_ANON_KEY=eyJ...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_AGENT_ID=agent_...

# Optional
MODEL=claude-3-sonnet-20240229
SYSTEM_PROMPT="Your custom prompt"
MCP_SERVERS=[]
```

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://...supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_URL=https://your-backend-url.com
```

## 📝 Post-Deployment Checklist

1. ✅ Backend API is accessible
   - Test: `curl https://your-backend-url/health`

2. ✅ Update ElevenLabs webhook URL
   - Go to ElevenLabs dashboard
   - Update tool URL to your production backend

3. ✅ Frontend environment variables
   - Update `VITE_API_URL` to production backend

4. ✅ Test the complete flow
   - Open frontend
   - Start voice chat
   - Ask for stock prices
   - Verify tool execution

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to git
2. **CORS**: Configure for production domains only
3. **Rate Limiting**: Implement rate limiting in production
4. **HTTPS**: Always use HTTPS in production
5. **Authentication**: Consider adding user authentication

## 🛠️ Maintenance

### Update Agent Personality
```bash
# Edit agent config
vi agent_configs/dev/gsves_market_insights.json

# Sync with ElevenLabs
export ELEVENLABS_API_KEY=your-key
convai sync --env dev
```

### Monitor Logs
```bash
# Fly.io
fly logs

# Docker
docker-compose logs -f

# Local
tail -f backend/logs/*.log
```

### Scale Services
```bash
# Fly.io
fly scale count 2  # Scale to 2 instances
fly scale vm shared-cpu-1x  # Change VM size
```

## 🚨 Troubleshooting

### Tool Not Working
1. Check webhook URL is public and accessible
2. Verify tool approval in ElevenLabs dashboard
3. Check backend logs for errors

### Voice Not Working
1. Verify ElevenLabs API key and Agent ID
2. Check browser microphone permissions
3. Ensure WebSocket connection is established

### Database Issues
1. Verify Supabase credentials
2. Check RLS policies in Supabase
3. Ensure tables are created (run schema.sql)

## 📞 Support

For issues or questions:
- Check logs first
- Review environment variables
- Test each component independently
- Contact support with error messages and logs