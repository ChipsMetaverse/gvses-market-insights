#!/bin/bash

# Fix ElevenLabs Agent LLM Configuration
# This ensures the agent has an LLM model selected

source backend/.env

AGENT_ID="${ELEVENLABS_AGENT_ID:-agent_4901k2tkkq54f4mvgpndm3pgzm7g}"
API_KEY="${ELEVENLABS_API_KEY}"

echo "🔧 Fixing LLM Configuration for ElevenLabs Agent"
echo "================================================"
echo "Agent ID: ${AGENT_ID}"

# Read the prompt
AGENT_PROMPT=$(cat idealagent.md)
AGENT_PROMPT_ESCAPED=$(echo "$AGENT_PROMPT" | jq -Rs .)

# Create comprehensive configuration with LLM settings
cat > /tmp/llm_fix.json << EOF
{
  "name": "Gsves Market Insights",
  "conversation_config": {
    "agent": {
      "prompt": {
        "prompt": ${AGENT_PROMPT_ESCAPED},
        "llm": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2500
      },
      "first_message": "",
      "language": "en"
    },
    "tts": {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "model_id": "eleven_turbo_v2_5",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": true
      },
      "pronunciation_dictionary_locators": []
    },
    "stt": {
      "model": "nova-2",
      "language": "en"
    },
    "turn": {
      "mode": "system_response_required",
      "threshold": 500
    }
  }
}
EOF

echo "📤 Sending LLM configuration update..."

# Update with full config including LLM
RESPONSE=$(curl -s -X PATCH \
  "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/llm_fix.json \
  -w "\nHTTP_STATUS:%{http_code}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "204" ]; then
    echo "✅ LLM configuration updated successfully!"
else
    echo "⚠️  Initial update returned status: $HTTP_STATUS"
    echo "Trying alternative configuration..."
    
    # Try simpler update focusing on prompt structure
    cat > /tmp/llm_simple.json << EOF
{
  "conversation_config": {
    "agent": {
      "prompt": ${AGENT_PROMPT_ESCAPED},
      "first_message": "",
      "language": "en",
      "llm": {
        "model": "gpt-4o-mini",
        "temperature": 0.7
      }
    }
  }
}
EOF

    RESPONSE2=$(curl -s -X PATCH \
      "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
      -H "xi-api-key: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d @/tmp/llm_simple.json \
      -w "\nHTTP_STATUS:%{http_code}")
    
    HTTP_STATUS2=$(echo "$RESPONSE2" | grep "HTTP_STATUS" | cut -d: -f2)
    
    if [ "$HTTP_STATUS2" = "200" ] || [ "$HTTP_STATUS2" = "204" ]; then
        echo "✅ Alternative configuration succeeded!"
    else
        echo "⚠️  API configuration has limitations. Manual configuration required."
    fi
fi

# Clean up
rm -f /tmp/llm_fix.json /tmp/llm_simple.json

echo ""
echo "🔍 Verifying configuration..."
sleep 2

# Get and check configuration
CONFIG=$(curl -s -X GET \
  "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}")

if echo "$CONFIG" | jq -e '.conversation_config.agent.prompt' > /dev/null 2>&1; then
    echo "✅ Agent prompt is configured"
fi

if echo "$CONFIG" | jq -e '.conversation_config.agent | has("llm") or has("prompt.llm")' > /dev/null 2>&1; then
    echo "✅ LLM settings detected"
else
    echo "⚠️  LLM may need manual configuration"
fi

echo ""
echo "📝 IMPORTANT: Due to API limitations, please verify in the dashboard:"
echo "1. Go to: https://elevenlabs.io/app/conversational-ai/agents/${AGENT_ID}"
echo "2. Click on 'Analysis' or 'Model' tab"
echo "3. Ensure an LLM is selected:"
echo "   - Recommended: GPT-4o-mini or GPT-4"
echo "   - Alternative: Claude 3.5 Sonnet"
echo "4. Set Temperature: 0.7"
echo "5. Set Max Tokens: 2500"
echo "6. Save changes"
echo ""
echo "Then test at: https://elevenlabs.io/app/talk-to?agent_id=${AGENT_ID}"