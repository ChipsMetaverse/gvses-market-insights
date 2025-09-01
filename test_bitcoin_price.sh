#!/bin/bash

echo "🧪 Testing Bitcoin Price Query"
echo "=============================="

# Get signed URL
SIGNED_URL=$(curl -s http://localhost:8000/elevenlabs/signed-url | jq -r '.signed_url')

echo "Asking: 'What is the current price of Bitcoin?'"
echo ""

# Send query and wait for response
(
    echo '{"type":"conversation_initiation_client_data"}'
    sleep 2
    echo '{"type":"user_message","text":"What is the current price of Bitcoin?"}'
    sleep 10
) | wscat -c "$SIGNED_URL" 2>/dev/null | while read -r line; do
    if echo "$line" | jq -e '.type == "agent_response"' > /dev/null 2>&1; then
        RESPONSE=$(echo "$line" | jq -r '.agent_response_event.agent_response')
        echo "🤖 Agent Response:"
        echo "$RESPONSE"
        echo ""
        
        # Check if response contains correct price range
        if echo "$RESPONSE" | grep -E "11[0-9],|112,|110,|thousand" > /dev/null; then
            echo "✅ SUCCESS: Agent is using real data (~$112,000)"
        elif echo "$RESPONSE" | grep -E "49\.|forty-nine" > /dev/null; then
            echo "❌ FAILURE: Agent is still hallucinating ($49)"
        else
            echo "⚠️  UNCLEAR: Check the price in the response"
        fi
    fi
done

echo ""
echo "=============================="
echo "Expected: Bitcoin at ~$112,000"
echo "Not: Bitcoin at $49"