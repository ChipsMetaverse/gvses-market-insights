# Computer Use Testing Instructions

## Setup Complete ✅

The Anthropic Computer Use Docker container is now running with the following services:

- **Combined Interface**: http://localhost:8080 (OPEN IN YOUR BROWSER)
- **Streamlit Chat**: http://localhost:8501
- **Desktop View**: http://localhost:6080/vnc.html
- **VNC Access**: vnc://localhost:5900

## How to Test with Trading Application

### Step 1: Open Computer Use Interface
1. Open your browser to: **http://localhost:8080**
2. You'll see a split interface:
   - Left side: Chat with Claude
   - Right side: Virtual desktop view

### Step 2: Test Voice Assistant Interaction

In the chat interface, type or paste this prompt:

```
Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load
4. Find the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (placeholder: "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit
8. Report what information was provided

As a professional trader with 30+ years of experience (G'sves persona), 
also provide insights on PLTR's current market position.
```

### Step 3: Advanced Testing Scenarios

Once the basic test works, try these scenarios:

#### Scenario A: Market Analysis
```
Using the Voice Assistant, ask:
"What's the latest news on Tesla? Show me the TSLA chart"
Then analyze the technical indicators visible on the chart.
```

#### Scenario B: Technical Analysis
```
Click on the chart and use the drawing tools to:
1. Draw a trendline on the TSLA chart
2. Add support and resistance levels
3. Ask the Voice Assistant about the technical setup
```

#### Scenario C: Multi-Symbol Navigation
```
Use the Voice Assistant to:
1. "Show me Microsoft stock" 
2. "Compare MSFT with GOOGL"
3. "What's moving in the market today?"
```

## What Computer Use Does

Computer Use allows Claude to:
- See the virtual desktop (screenshots)
- Control the mouse (click, drag)
- Type on the keyboard
- Navigate web applications
- Interact with UI elements
- Perform complex multi-step tasks

## Monitoring the Interaction

1. **Chat Panel**: Shows Claude's reasoning and actions
2. **Desktop View**: Shows real-time mouse movements and interactions
3. **Action Log**: Each action Claude takes is logged in the chat

## Troubleshooting

If Computer Use seems stuck:
1. Click "Stop" in the interface
2. Refresh the browser (F5)
3. Start with a simpler task first

If the trading app doesn't load:
1. Verify it's running: `curl http://localhost:5174`
2. Check frontend is built: `cd frontend && npm run build`
3. Restart frontend: `cd frontend && npm run dev`

## Docker Container Management

```bash
# View logs
docker logs computer-use-demo -f

# Stop container
docker stop computer-use-demo

# Remove container
docker rm computer-use-demo

# Restart container
docker restart computer-use-demo
```

## Notes

- The virtual desktop runs at 1024x768 resolution
- Firefox is pre-installed in the container
- Computer Use will take screenshots and analyze them before each action
- Each interaction may take a few seconds as Claude processes the visual information

## Success Criteria

✅ Computer Use successfully navigates to localhost:5174
✅ Finds and clicks the Voice Assistant input field  
✅ Types a market-related question
✅ Receives and reports the response
✅ Can interact with charts and UI elements