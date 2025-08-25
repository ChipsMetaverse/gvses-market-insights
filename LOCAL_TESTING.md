# Local Testing Guide

## ✅ What's Now Available

### 1. **Mode Switcher** (UI Control)
Located at the top of the voice section:
- **💬 Conversation Mode**: Quick 1-2 sentence responses
- **📊 Overview Mode**: Detailed analysis with technical levels

### 2. **Text Input**
The VoiceAssistantElevenlabs component includes:
- Text input field at the bottom
- Send button to submit typed messages  
- Works alongside voice input

### 3. **Voice Commands**
- Click "Start Voice Chat" to begin
- Hold the microphone button to speak
- Or type messages in the text input

## 🏠 Local Environment Setup

### Backend (Port 8000)
```bash
cd backend
python mcp_server.py
```
- Handles ElevenLabs signed URL generation
- Proxies API requests
- Manages conversation history

### Frontend (Port 5173)
```bash
cd frontend  
npm run dev
```
- React app with trading dashboard
- Real-time voice interaction
- Chart visualization

## ⚠️ Local Testing Considerations

### ✅ What Works Locally:
1. **Voice Conversations** - Full ElevenLabs integration
2. **Text Input** - Send typed messages
3. **Mode Switching** - Toggle between conversation/overview
4. **Stock Data** - Real-time prices and charts
5. **Technical Levels** - QE, ST, LTB calculations

### ⚡ Potential Local Issues:

1. **Browser Permissions**
   - Microphone access required for voice
   - Allow permissions when prompted

2. **HTTPS Requirements**
   - ElevenLabs WebSocket may require secure connection
   - Browser may block mixed content
   - Solution: Use Chrome with `--allow-insecure-localhost` flag

3. **CORS Issues**
   - Backend configured for localhost:5173
   - If frontend port changes, update backend CORS settings

4. **API Keys**
   Ensure these are set in `backend/.env`:
   ```
   ELEVENLABS_API_KEY=your_key
   ELEVENLABS_AGENT_ID=your_agent_id
   ANTHROPIC_API_KEY=your_key
   SUPABASE_URL=your_url
   SUPABASE_ANON_KEY=your_key
   ```

## 🎯 How to Test

### Voice Mode:
1. Click "Start Voice Chat"
2. Allow microphone permission
3. Say: "How's Tesla doing?"
4. Get quick response: "TSLA at $245, up 3.2%"

### Text Mode:
1. Type in the input field: "What's Apple at?"
2. Press Send or Enter
3. Get response in chat

### Mode Switching:
1. **Conversation Mode**: Ask "How's the market?"
   - Response: "SPY up 1.2%. Tech leading gains."

2. **Overview Mode**: Say "Give me full analysis on NVDA"
   - Response: Detailed technical analysis with levels, trade setup, options plays

### Voice Commands for Mode Switch:
- Say "overview" or "full analysis" to switch to detailed mode
- Say "quick mode" or "conversation" to return to brief responses

## 🔧 Troubleshooting

### No Voice Response:
1. Check browser console for WebSocket errors
2. Verify ElevenLabs agent is configured
3. Ensure API keys are valid

### Chart Not Loading:
1. Check if backend is running (port 8000)
2. Verify market data API is accessible
3. Check browser console for errors

### Text Input Missing:
1. Component should be visible below voice controls
2. If not visible, check CSS conflicts
3. Ensure VoiceAssistantElevenlabs is imported

## 📝 Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Microphone permission granted
- [ ] Can start voice chat
- [ ] Can send text messages
- [ ] Mode switcher visible and functional
- [ ] Chart loads with real data
- [ ] Technical levels display correctly
- [ ] Voice responses match selected mode

## 🚀 Next Steps

Once local testing is complete:
1. Deploy backend to Fly.io or similar
2. Update frontend API URL to production
3. Deploy frontend to Vercel
4. Test production environment