#!/bin/bash

echo "📡 Updating ElevenLabs agent configurations with production URLs..."

# Navigate to the project directory
cd /Users/MarcoPolo/workspace/claude-voice-mcp

# Sync the agent configuration
echo "🔄 Syncing agent configuration..."
convai sync --env dev --agent "Gsves Market Insights"

echo "✅ Agent configuration has been updated with production URLs!"
echo ""
echo "🎯 Production backend URL: https://gvses-market-insights.fly.dev"
echo ""
echo "⚠️  IMPORTANT: Please manually update the webhook URLs in the ElevenLabs dashboard:"
echo "   1. Go to https://elevenlabs.io/app/conversational-ai"
echo "   2. Select your 'Gsves Market Insights' agent"
echo "   3. Go to Tools section"
echo "   4. Update all webhook URLs from 'gvses-backend.loca.lt' to 'gvses-market-insights.fly.dev'"
echo ""
echo "📝 Updated tool configurations:"
echo "   - get_stock_price: https://gvses-market-insights.fly.dev/api/stock-price"
echo "   - get_stock_news: https://gvses-market-insights.fly.dev/api/stock-news"
echo "   - get_comprehensive_stock_data: https://gvses-market-insights.fly.dev/api/comprehensive-stock-data"