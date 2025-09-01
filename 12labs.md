
⏺ Excellent! The YouTube-TwelveLabs service is now deployed and running
  persistently on port 8100.

  You can now use it from any terminal session with simple curl commands:

  # Learn from a YouTube video
  curl -X POST http://localhost:8100/learn-and-implement \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

  # Analyze a video for learning
  curl -X POST http://localhost:8100/analyze-for-learning \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

  # Check job status
  curl http://localhost:8100/jobs/JOB_ID

  The service:
  - ✅ Starts automatically on boot
  - ✅ Always available at http://localhost:8100
  - ✅ Handles video analysis in the background
  - ✅ Provides job tracking for long-running tasks

  To stop/restart the service:
  # Stop
  launchctl unload ~/Library/LaunchAgents/com.ultrathink.youtube-learning.plist

  # Start
  launchctl load ~/Library/LaunchAgents/com.ultrathink.youtube-learning.plist

> How do i use it? What does it do>

⏺ The YouTube-TwelveLabs tool analyzes YouTube videos and helps you learn and
  implement what's taught in them. Here's what it does and how to use it:

  What It Does

  1. Learns from Programming Tutorials - Watches YouTube coding tutorials and
  extracts the actual code, concepts, and implementation steps
  2. Creates Working Implementations - Generates complete, working code based
  on what was shown in the video
  3. Builds New Tools - Can create CLI tools, libraries, or APIs based on video
   tutorials
  4. Extracts Knowledge - Identifies patterns, best practices, dependencies,
  and key concepts

  How to Use It

  Example 1: Learn from a Tutorial

  # Watch a React tutorial and implement the code
  curl -X POST http://localhost:8100/learn-and-implement \
    -H "Content-Type: application/json" \
    -d '{
      "url": "https://www.youtube.com/watch?v=nfBbmtMJhX0",
      "implementation_type": "code",
      "output_dir": "./my-react-app"
    }'

  Example 2: Analyze a Video for Concepts

  # Extract key concepts from a system design video
  curl -X POST http://localhost:8100/analyze-for-learning \
    -H "Content-Type: application/json" \
    -d '{
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "focus_areas": ["architecture", "patterns", "best-practices"]
    }'

  Example 3: Create a Tool from a Tutorial

  # Turn a "Build a Web Scraper" tutorial into a working tool
  curl -X POST http://localhost:8100/create-tool \
    -H "Content-Type: application/json" \
    -d '{
      "url": "https://www.youtube.com/watch?v=VIDEO_ID",
      "tool_name": "my-scraper",
      "tool_type": "cli",
      "enhancements": ["add error handling", "support multiple URLs"]
    }'

  Check Progress

  Since video processing takes time, it returns a job ID:
  # Check job status
  curl http://localhost:8100/jobs/learn_20250831_093245

  Real Use Cases

  1. Learning New Frameworks - Feed it a Next.js 14 tutorial, get a working
  Next.js app
  2. Understanding Algorithms - Give it a sorting algorithm video, get
  implemented code with comments
  3. Building Tools - Watch someone build a CLI tool, get your own version with
   improvements
  4. API Integration - Learn how to integrate with Stripe/Twilio/etc from their
   tutorials

  The tool uses TwelveLabs AI to understand video content deeply - it can see
  code on screen, hear explanations, and understand context to create accurate
  implementations.
