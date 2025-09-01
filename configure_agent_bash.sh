#!/bin/bash

# ElevenLabs Agent Configuration Script
# Configures the agent using API calls

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE} ElevenLabs Agent Configuration via API${NC}"
echo -e "${BLUE}============================================================${NC}"

# Load environment variables
source backend/.env

AGENT_ID="${ELEVENLABS_AGENT_ID:-agent_4901k2tkkq54f4mvgpndm3pgzm7g}"
API_KEY="${ELEVENLABS_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ ELEVENLABS_API_KEY not found in backend/.env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API Key found${NC}"
echo -e "Agent ID: ${AGENT_ID}"

# Read the ideal agent prompt
AGENT_PROMPT=$(cat idealagent.md)

# Escape the prompt for JSON
AGENT_PROMPT_ESCAPED=$(echo "$AGENT_PROMPT" | jq -Rs .)

echo -e "\n${YELLOW}📡 Fetching current agent configuration...${NC}"

# Get current agent config
CURRENT_CONFIG=$(curl -s -X GET \
  "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Current configuration retrieved${NC}"
    echo "$CURRENT_CONFIG" | jq -r '.name' | xargs -I {} echo "   Name: {}"
else
    echo -e "${RED}❌ Failed to fetch current configuration${NC}"
fi

echo -e "\n${YELLOW}📤 Updating agent configuration...${NC}"

# Create the update payload
cat > /tmp/agent_update.json << EOF
{
  "conversation_config": {
    "agent": {
      "prompt": ${AGENT_PROMPT_ESCAPED},
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
      }
    },
    "stt": {
      "model": "nova-2",
      "language": "en"
    }
  }
}
EOF

# Update the agent
UPDATE_RESPONSE=$(curl -s -X PATCH \
  "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/agent_update.json)

UPDATE_STATUS=$?

if [ $UPDATE_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Configuration update sent${NC}"
else
    echo -e "${YELLOW}⚠️  Update request completed with warnings${NC}"
fi

echo -e "\n${YELLOW}🔍 Verifying update...${NC}"

# Verify the update
sleep 2
VERIFY_CONFIG=$(curl -s -X GET \
  "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json")

if echo "$VERIFY_CONFIG" | grep -q "G'sves\|Gsves"; then
    echo -e "${GREEN}✅ G'sves prompt detected in configuration${NC}"
else
    echo -e "${YELLOW}⚠️  G'sves prompt may need manual verification${NC}"
fi

# Check voice configuration
if echo "$VERIFY_CONFIG" | grep -q "voice_id"; then
    echo -e "${GREEN}✅ Voice is configured${NC}"
else
    echo -e "${RED}❌ Voice needs configuration${NC}"
fi

# Clean up
rm -f /tmp/agent_update.json

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE} Configuration Complete${NC}"
echo -e "${BLUE}============================================================${NC}"

echo -e "\n${GREEN}📊 Next Steps:${NC}"
echo "1. Test the agent at:"
echo "   https://elevenlabs.io/app/talk-to?agent_id=${AGENT_ID}"
echo ""
echo "2. Run the test script:"
echo "   python3 test_elevenlabs_conversation.py"
echo ""
echo "3. Test in the app:"
echo "   - Open http://localhost:5174"
echo "   - Click 'Start Voice Chat'"
echo ""

# Optional: Test the agent directly via API
echo -e "\n${YELLOW}🧪 Quick API Test:${NC}"
echo "Testing agent response..."

# Get signed URL for testing
SIGNED_URL_RESPONSE=$(curl -s -X GET \
  "https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id=${AGENT_ID}" \
  -H "xi-api-key: ${API_KEY}")

if [ $? -eq 0 ]; then
    SIGNED_URL=$(echo "$SIGNED_URL_RESPONSE" | jq -r '.signed_url')
    if [ ! -z "$SIGNED_URL" ] && [ "$SIGNED_URL" != "null" ]; then
        echo -e "${GREEN}✅ Agent is responding to API calls${NC}"
        echo "   Signed URL generated successfully"
    else
        echo -e "${RED}❌ Could not generate signed URL${NC}"
    fi
else
    echo -e "${RED}❌ API test failed${NC}"
fi

echo -e "\n${GREEN}✨ Configuration script completed!${NC}"