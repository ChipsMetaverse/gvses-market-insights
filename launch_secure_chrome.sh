#!/bin/bash

# Launch Chrome with disabled security for local development
# This allows HTTP to WSS connections

echo "Launching Chrome with disabled security for ElevenLabs WebSocket..."
echo "This is for development only!"
echo ""

# Kill any existing Chrome instances first
killall "Google Chrome" 2>/dev/null || true

# Wait a moment
sleep 1

# Launch Chrome with disabled security
open -a "Google Chrome" \
  --args \
  --allow-insecure-localhost \
  --ignore-certificate-errors \
  --disable-web-security \
  --disable-features=IsolateOrigins,site-per-process \
  --user-data-dir="/tmp/chrome-dev-elevenlabs" \
  "http://localhost:5174"

echo ""
echo "Chrome launched! The voice chat should now work."
echo "Click the Voice Control button to connect."