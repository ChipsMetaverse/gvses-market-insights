#!/bin/bash

# Test ElevenLabs Agent with Market Query
# Verifies the agent can provide stock market information

echo "📈 ElevenLabs Market Query Test"
echo "==============================="

# Get signed URL
SIGNED_URL=$(curl -s http://localhost:8000/elevenlabs/signed-url | jq -r '.signed_url')

if [ -z "$SIGNED_URL" ] || [ "$SIGNED_URL" = "null" ]; then
    echo "❌ Failed to get signed URL"
    exit 1
fi

echo "✅ Connected to ElevenLabs"
echo ""
echo "Sending market queries..."
echo ""

# Test multiple market queries
QUERIES=(
    "What is the current price of Apple stock?"
    "Give me the price of Bitcoin"
    "How is the S&P 500 doing today?"
)

for query in "${QUERIES[@]}"; do
    echo "📊 Query: \"$query\""
    echo "-----------------------------------"
    
    (
        echo '{"type":"conversation_initiation_client_data"}'
        sleep 1
        echo "{\"type\":\"user_message\",\"text\":\"$query\"}"
        sleep 6
    ) | wscat -c "$SIGNED_URL" 2>/dev/null | while read -r line; do
        if echo "$line" | jq -e '.type == "agent_response"' > /dev/null 2>&1; then
            RESPONSE=$(echo "$line" | jq -r '.agent_response_event.agent_response')
            echo "💬 Response:"
            echo "$RESPONSE" | sed 's/^/   /'
            echo ""
            break
        elif echo "$line" | jq -e '.type == "audio"' > /dev/null 2>&1; then
            echo -n "🔊"
        fi
    done
    
    sleep 2
done

echo "==============================="
echo "✅ Market query test complete!"
echo ""
echo "The agent should have provided real-time market data for:"
echo "• Apple (AAPL) stock price"
echo "• Bitcoin (BTC) price"  
echo "• S&P 500 index performance"