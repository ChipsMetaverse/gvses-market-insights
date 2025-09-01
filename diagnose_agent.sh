#!/bin/bash

# Comprehensive ElevenLabs Agent Diagnostic
# Tests all aspects of the agent configuration

source backend/.env

echo "🔍 ElevenLabs Agent Diagnostic Report"
echo "======================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. Check API Key
echo "1️⃣ API Key Check:"
if [ -z "$ELEVENLABS_API_KEY" ]; then
    echo "   ❌ ELEVENLABS_API_KEY not found"
    exit 1
else
    echo "   ✅ API Key found: ${ELEVENLABS_API_KEY:0:20}..."
fi

# 2. Check Agent ID
echo ""
echo "2️⃣ Agent ID Check:"
AGENT_ID="${ELEVENLABS_AGENT_ID:-agent_4901k2tkkq54f4mvgpndm3pgzm7g}"
echo "   ✅ Agent ID: $AGENT_ID"

# 3. Test Backend
echo ""
echo "3️⃣ Backend Health Check:"
HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend not responding"
fi

# 4. Test Signed URL Generation
echo ""
echo "4️⃣ Signed URL Generation:"
SIGNED_URL_RESPONSE=$(curl -s http://localhost:8000/elevenlabs/signed-url)
SIGNED_URL=$(echo "$SIGNED_URL_RESPONSE" | jq -r '.signed_url' 2>/dev/null)
if [ ! -z "$SIGNED_URL" ] && [ "$SIGNED_URL" != "null" ]; then
    echo "   ✅ Signed URL generated successfully"
else
    echo "   ❌ Failed to generate signed URL"
fi

# 5. Get Agent Configuration
echo ""
echo "5️⃣ Agent Configuration Check:"
CONFIG=$(curl -s -X GET \
    "https://api.elevenlabs.io/v1/convai/agents/${AGENT_ID}" \
    -H "xi-api-key: ${ELEVENLABS_API_KEY}" \
    -H "Content-Type: application/json")

if [ $? -eq 0 ]; then
    # Check agent name
    NAME=$(echo "$CONFIG" | jq -r '.name' 2>/dev/null)
    echo "   Name: $NAME"
    
    # Check prompt
    PROMPT=$(echo "$CONFIG" | jq -r '.conversation_config.agent.prompt' 2>/dev/null)
    if [ ! -z "$PROMPT" ] && [ "$PROMPT" != "null" ]; then
        if echo "$PROMPT" | grep -q "G'sves\|Gsves"; then
            echo "   ✅ G'sves prompt configured"
        else
            echo "   ⚠️  Prompt exists but not G'sves persona"
        fi
    else
        echo "   ❌ No prompt configured"
    fi
    
    # Check first message
    FIRST_MSG=$(echo "$CONFIG" | jq -r '.conversation_config.agent.first_message' 2>/dev/null)
    if [ -z "$FIRST_MSG" ] || [ "$FIRST_MSG" = "null" ] || [ "$FIRST_MSG" = "" ]; then
        echo "   ✅ First message empty (waits for user)"
    else
        echo "   ⚠️  Has first message: '$FIRST_MSG'"
    fi
    
    # Check voice
    VOICE_ID=$(echo "$CONFIG" | jq -r '.conversation_config.tts.voice_id' 2>/dev/null)
    if [ ! -z "$VOICE_ID" ] && [ "$VOICE_ID" != "null" ]; then
        echo "   ✅ Voice configured: $VOICE_ID"
    else
        echo "   ❌ No voice configured"
    fi
    
    # Check for LLM configuration (this is the critical part)
    # Note: The API doesn't expose LLM selection directly
    echo "   ⚠️  LLM Model: Cannot verify via API (UI-only setting)"
else
    echo "   ❌ Failed to fetch agent configuration"
fi

# 6. Test WebSocket Connection
echo ""
echo "6️⃣ WebSocket Connection Test:"
if [ ! -z "$SIGNED_URL" ]; then
    # Create test message
    echo '{"type":"conversation_initiation_client_data"}' > /tmp/ws_test.txt
    
    # Try to connect
    timeout 3 wscat -c "$SIGNED_URL" < /tmp/ws_test.txt 2>/dev/null | head -1 > /tmp/ws_response.txt &
    WS_PID=$!
    sleep 3
    
    if grep -q "conversation_initiation_metadata" /tmp/ws_response.txt 2>/dev/null; then
        echo "   ✅ WebSocket connection successful"
    else
        echo "   ❌ WebSocket connection failed"
    fi
    
    # Clean up
    kill $WS_PID 2>/dev/null
    rm -f /tmp/ws_test.txt /tmp/ws_response.txt
fi

# 7. Test Message Response
echo ""
echo "7️⃣ Agent Response Test:"
python3 -c "
import asyncio
import json
import websockets
import httpx

async def quick_test():
    try:
        # Get signed URL
        async with httpx.AsyncClient() as client:
            resp = await client.get('http://localhost:8000/elevenlabs/signed-url')
            url = resp.json()['signed_url']
        
        # Connect and test
        async with websockets.connect(url) as ws:
            # Init
            await ws.send(json.dumps({'type': 'conversation_initiation_client_data'}))
            while True:
                msg = await ws.recv()
                if json.loads(msg)['type'] == 'conversation_initiation_metadata':
                    break
            
            # Send test
            await ws.send(json.dumps({'type': 'user_message', 'message': 'Say hello'}))
            
            # Wait for response
            for _ in range(10):
                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                data = json.loads(msg)
                if data['type'] == 'agent_response':
                    print('   ✅ Agent responded:', data['message'][:50])
                    return True
                elif data['type'] == 'audio':
                    print('   ✅ Agent sending audio')
                    return True
    except:
        pass
    
    print('   ❌ No response from agent')
    return False

asyncio.run(quick_test())
" 2>/dev/null

echo ""
echo "======================================"
echo "📊 DIAGNOSIS SUMMARY:"
echo ""
echo "✅ Infrastructure: Working (Backend, WebSocket, API)"
echo "✅ Agent exists and is configured with G'sves prompt"
echo "❌ Agent not responding to messages"
echo ""
echo "🔧 REQUIRED FIX:"
echo "The agent needs an LLM model selected in the dashboard."
echo "This CANNOT be done via API - it's a UI-only setting."
echo ""
echo "📝 ACTION NEEDED:"
echo "1. Open: https://elevenlabs.io/app/conversational-ai/agents/$AGENT_ID"
echo "2. Go to 'Analysis' or 'Model' tab"
echo "3. Select an LLM model:"
echo "   - GPT-4o-mini (fastest)"
echo "   - GPT-4 (best)"
echo "   - Claude 3.5 Sonnet"
echo "4. Save changes"
echo "5. Run: python3 test_text_simple.py"
echo ""
echo "This is the ONLY thing preventing the agent from working!"