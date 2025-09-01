#!/bin/bash

echo "🧪 Testing ElevenLabs Knowledge Base Queries"
echo "==========================================="

# Get signed URL
SIGNED_URL=$(curl -s http://localhost:8000/elevenlabs/signed-url | jq -r '.signed_url')

# Test queries that should trigger knowledge base
QUERIES=(
    "What are the GVSES trading guidelines?"
    "Explain what LTB means in trading"
    "What does the Encyclopedia of Chart Patterns say?"
    "According to your knowledge base, what is good risk management?"
)

for query in "${QUERIES[@]}"; do
    echo ""
    echo "📝 Testing: $query"
    echo "---"
    
    # Send query and capture response
    (
        echo '{"type":"conversation_initiation_client_data"}'
        sleep 2
        echo "{\"type\":\"user_message\",\"text\":\"$query\"}"
        sleep 8
    ) | wscat -c "$SIGNED_URL" 2>/dev/null | while read -r line; do
        if echo "$line" | jq -e '.type == "agent_response"' > /dev/null 2>&1; then
            RESPONSE=$(echo "$line" | jq -r '.agent_response_event.agent_response')
            
            # Check for knowledge base indicators
            if echo "$RESPONSE" | grep -iE "guidelines|LTB|ST|QE|chart pattern|risk management|encyclopedia|trading bible" > /dev/null; then
                echo "✅ Knowledge base content detected!"
            else
                echo "⚠️  No clear knowledge base reference"
            fi
            
            # Show first 200 chars of response
            echo "Response: ${RESPONSE:0:200}..."
            break
        fi
    done
    
    sleep 2
done

echo ""
echo "==========================================="
echo "✅ Knowledge base query test complete"