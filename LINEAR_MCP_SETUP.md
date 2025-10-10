# Linear MCP Setup Guide

## Status: Configuration Needed

Linear MCP has been added to your Claude configuration but requires an API key to connect.

## Setup Steps

### 1. Get Your Linear API Key

1. **Create a Linear Account** (if you don't have one):
   - Go to https://linear.app
   - Sign up for free

2. **Generate API Key**:
   - Go to https://linear.app/settings/api
   - Click "Create API Key"
   - Give it a name like "Claude MCP"
   - Copy the API key (starts with `lin_api_`)

### 2. Configure Linear MCP

Once you have your API key, run this command:

```bash
claude mcp add linear npx -e LINEAR_API_TOKEN=YOUR_API_KEY_HERE -- -y @tacticlaunch/mcp-linear
```

Replace `YOUR_API_KEY_HERE` with your actual Linear API key.

### 3. Alternative: Use Without Linear Account

If you don't want to use Linear's cloud service, you can:

1. **Remove Linear MCP**:
   ```bash
   claude mcp remove linear
   ```

2. **Use Local Alternative**:
   - Consider using a local task management system
   - Or use GitHub Issues (already configured with GitHub MCP)

## Current Configuration

Linear MCP is added but not connected because it needs an API key:
- Package: @tacticlaunch/mcp-linear
- Status: ✗ Failed to connect (No API key)

## Benefits Once Connected

With Linear MCP, you'll be able to:
- Create issues automatically when bugs are found
- Track features and tasks
- Generate sprint plans
- Update issue status
- Add comments and attachments
- Search and filter issues

## Using Linear MCP in Claude

Once configured with an API key, you can use commands like:
- "Create a Linear issue for this bug"
- "Show my Linear tasks"
- "Update Linear issue #123 as completed"
- "Add this to the backlog in Linear"

## Alternative: Use GitHub Issues Instead

Since you already have GitHub MCP configured and working, you can achieve similar project management using GitHub Issues:

```bash
# GitHub MCP is already working and can:
# - Create issues
# - Manage projects
# - Track milestones
# - Add labels and assignees
```

## Decision Required

Would you like to:
1. **Sign up for Linear** and get an API key (Recommended for full "Vibe Coding" workflow)
2. **Use GitHub Issues** instead (Already working, no additional setup needed)
3. **Skip project management MCP** for now

Let me know your preference!