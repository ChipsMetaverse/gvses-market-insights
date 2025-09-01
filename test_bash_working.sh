#!/bin/bash

# ElevenLabs Agent Text Test Using Bash
# Sends text message and waits for response

echo "🧪 ElevenLabs Bash Test"
echo "======================="

# Get signed URL from backend
echo "📡 Getting signed URL..."
SIGNED_URL=$(curl -s http://localhost:8000/elevenlabs/signed-url | jq -r '.signed_url')

if [ -z "$SIGNED_URL" ] || [ "$SIGNED_URL" = "null" ]; then
    echo "❌ Failed to get signed URL"
    exit 1
fi

echo "✅ Got signed URL"
echo ""

# Create test with wscat
echo "📤 Sending test message via WebSocket..."
echo "Test message: 'What is 2 plus 2?'"
echo ""
echo "🎯 Agent Response:"
echo "=================="

# Use wscat with proper JSON parsing
(
    echo '{"type":"conversation_initiation_client_data"}'
    sleep 2
    echo '{"type":"user_message","text":"What is 2 plus 2?"}'
    sleep 8  # Wait for response
) | wscat -c "$SIGNED_URL" 2>/dev/null | while read -r line; do
    # Check if line contains agent_response
    if echo "$line" | jq -e '.type == "agent_response"' > /dev/null 2>&1; then
        RESPONSE=$(echo "$line" | jq -r '.agent_response_event.agent_response')
        echo ""
        echo "💬 Agent says:"
        echo "   $RESPONSE"
        echo ""
    elif echo "$line" | jq -e '.type == "audio"' > /dev/null 2>&1; then
        echo -n "🔊"
    elif echo "$line" | jq -e '.type == "conversation_initiation_metadata"' > /dev/null 2>&1; then
        echo "✅ Connected and initialized"
    elif echo "$line" | jq -e '.type == "ping"' > /dev/null 2>&1; then
        # Ignore ping messages
        :
    fi
done

echo ""
echo "=================="
echo "✅ Test complete!"
echo ""
echo "If you saw the agent response above, the agent is working correctly!"
echo "The agent should have answered: 'What is 2 plus 2?'"