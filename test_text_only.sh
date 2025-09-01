#!/bin/bash

# Test ElevenLabs Agent with Text Input Only
# Uses wscat to connect and send messages

echo "🧪 ElevenLabs Text-Only Test"
echo "============================"

# Get signed URL from backend
echo "📡 Getting signed URL from backend..."
RESPONSE=$(curl -s http://localhost:8000/elevenlabs/signed-url)

if [ $? -ne 0 ]; then
    echo "❌ Failed to get signed URL from backend"
    echo "   Make sure backend is running on port 8000"
    exit 1
fi

SIGNED_URL=$(echo "$RESPONSE" | jq -r '.signed_url')

if [ -z "$SIGNED_URL" ] || [ "$SIGNED_URL" = "null" ]; then
    echo "❌ Invalid signed URL received"
    echo "   Response: $RESPONSE"
    exit 1
fi

echo "✅ Got signed URL"
echo "   URL: ${SIGNED_URL:0:80}..."

# Create a temporary file for messages
MESSAGES_FILE="/tmp/elevenlabs_messages.txt"
cat > "$MESSAGES_FILE" << EOF
{"type":"conversation_initiation_client_data"}
{"type":"user_message","text":"Hello, what is the current price of Tesla stock?"}
EOF

echo ""
echo "📤 Connecting to ElevenLabs WebSocket..."
echo "   Sending test message: 'Hello, what is the current price of Tesla stock?'"
echo ""
echo "🎯 Agent Response:"
echo "=================="

# Connect with wscat and send messages
# -x flag exits after a timeout
# We pipe the messages file and capture output
timeout 10 cat "$MESSAGES_FILE" | wscat -c "$SIGNED_URL" 2>/dev/null | while IFS= read -r line; do
    # Parse JSON responses
    if echo "$line" | jq -e '.type == "agent_response"' > /dev/null 2>&1; then
        MESSAGE=$(echo "$line" | jq -r '.message')
        echo "💬 Agent: $MESSAGE"
    elif echo "$line" | jq -e '.type == "audio"' > /dev/null 2>&1; then
        echo "🔊 [Audio chunk received]"
    elif echo "$line" | jq -e '.type == "conversation_initiation_metadata"' > /dev/null 2>&1; then
        echo "✅ [Conversation initialized]"
    elif echo "$line" | jq -e '.type == "user_transcript"' > /dev/null 2>&1; then
        TRANSCRIPT=$(echo "$line" | jq -r '.message')
        echo "👤 User transcript: $TRANSCRIPT"
    fi
done

# Clean up
rm -f "$MESSAGES_FILE"

echo ""
echo "=================="
echo "✅ Test complete"
echo ""
echo "If no agent response was shown above, the agent may not have an LLM configured."
echo "Check: https://elevenlabs.io/app/conversational-ai/agents/agent_4901k2tkkq54f4mvgpndm3pgzm7g"