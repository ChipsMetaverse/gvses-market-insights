# Computer Use - Accessing Host Application

## Important: Network Access from Docker Container

The Computer Use Docker container cannot access `localhost:5174` directly because localhost inside the container refers to the container itself, not your host machine.

## Solution: Use host.docker.internal

Instead of `localhost:5174`, use: **`host.docker.internal:5174`**

## Updated Test Prompt for Computer Use Interface

Go to http://localhost:8080 and paste this in the chat:

```
Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load (it may take a few seconds)
4. Look for the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (it has placeholder text "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit the message
8. Wait for the response to appear
9. Report what information was provided about PLTR

As a professional trader with 30+ years of experience (G'sves persona), 
also provide insights on PLTR's current market position.
```

## Why This Works

- **host.docker.internal** is a special DNS name that Docker provides
- It resolves to the host machine's IP address
- This allows the container to access services running on the host
- Works on Docker Desktop for Mac and Windows

## Verification Steps

1. In the Computer Use interface, you should see:
   - Firefox opening in the virtual desktop
   - Navigation to the trading app URL
   - The trading dashboard loading with charts
   - Claude clicking on the Voice Assistant input
   - Text being typed and submitted
   - Response appearing in the chat

## Alternative if host.docker.internal doesn't work

If for some reason host.docker.internal doesn't work, you can use your machine's local IP:

```bash
# Find your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Then use it in the URL, e.g.:
# http://192.168.1.100:5174
```