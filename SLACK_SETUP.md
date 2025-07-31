# Slack Integration Setup Guide

This guide will help you set up Slack integration to trigger your AI agent directly from Slack using slash commands.

## 🚀 Quick Overview

Once configured, you'll be able to use these commands in Slack:

- `/agent run` - Trigger intelligence digest
- `/agent run force` - Force run even if recent
- `/agent run test` - Dry run (no notifications)
- `/agent status [job_id]` - Check job status
- `/agent jobs` - List recent jobs
- `/agent help` - Show help

## 📱 Step 1: Create a Slack App

1. **Go to [Slack API](https://api.slack.com/apps)**
2. **Click "Create New App"**
3. **Choose "From scratch"**
4. **Enter app details:**
   - App Name: `Aircall Intelligence Agent`
   - Workspace: Choose your workspace
5. **Click "Create App"**

## ⚙️ Step 2: Configure Slash Commands

1. **In your app settings, go to "Slash Commands"**
2. **Click "Create New Command"**
3. **Configure the command:**
   - Command: `/agent`
   - Request URL: `https://your-deployed-api.com/slack/command`
   - Short Description: `Trigger AI competitive intelligence agent`
   - Usage Hint: `run [force|test] | status [job_id] | jobs | help`
4. **Click "Save"**

## 🔒 Step 3: Set Up Authentication

### Option A: Basic Setup (Skip signature verification)
Set this environment variable on your deployed API:
```bash
SLACK_SIGNING_SECRET=""  # Leave empty to skip verification
```

### Option B: Secure Setup (Recommended)
1. **In your Slack app settings, go to "Basic Information"**
2. **Copy the "Signing Secret"**
3. **Set environment variable on your deployed API:**
   ```bash
   SLACK_SIGNING_SECRET="your_signing_secret_here"
   ```

## 🎯 Step 4: Configure Permissions & Scopes

1. **Go to "OAuth & Permissions"**
2. **Add these Bot Token Scopes:**
   - `commands` - Use slash commands
   - `chat:write` - Send messages
   - `chat:write.public` - Send messages to channels
3. **Install the app to your workspace**
4. **Copy the "Bot User OAuth Token" (starts with `xoxb-`)**

## 🔧 Step 5: Deploy Your API

### Deploy with Slack Environment Variables

Make sure your deployed API has these environment variables:

```bash
# Required
API_KEY="your-secure-api-key"
OPENAI_API_KEY="your-openai-key"

# Slack Integration
SLACK_SIGNING_SECRET="your-slack-signing-secret"
SLACK_BOT_TOKEN="xoxb-your-bot-token"  # Optional: for advanced features

# Optional
TWITTER_BEARER_TOKEN="your-twitter-token"
```

### Update Deployment Configurations

**For Render.com - add to `render.yaml`:**
```yaml
envVars:
  - key: SLACK_SIGNING_SECRET
    sync: false  # Set manually in dashboard
  - key: SLACK_BOT_TOKEN  
    sync: false  # Set manually in dashboard
```

**For Fly.io:**
```bash
fly secrets set SLACK_SIGNING_SECRET="your-signing-secret"
fly secrets set SLACK_BOT_TOKEN="xoxb-your-bot-token"
```

**For Docker Compose - add to `.env`:**
```bash
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_BOT_TOKEN=xoxb-your-bot-token
```

## 🧪 Step 6: Test the Integration

1. **In any Slack channel, type:**
   ```
   /agent help
   ```

2. **You should see the help message with available commands**

3. **Try triggering the agent:**
   ```
   /agent run test
   ```

4. **Check the status:**
   ```
   /agent status [job-id-from-previous-command]
   ```

## 🎛️ Advanced: Interactive Components (Optional)

If you want buttons and interactive elements:

1. **Go to "Interactivity & Shortcuts"**
2. **Enable Interactivity**
3. **Set Request URL:** `https://your-deployed-api.com/slack/interactive`
4. **Save Changes**

## 🛠️ Usage Examples

### Basic Commands

```bash
# Show help
/agent help

# Trigger agent (respects recent run check)
/agent run

# Force run even if recent
/agent run force

# Test run (dry run, no notifications)
/agent run test

# Check specific job status
/agent status abc123de

# List recent jobs
/agent jobs

# Check your recent jobs only
/agent status
```

### Command Combinations

```bash
# Force test run with verbose output
/agent run force test verbose

# Regular test run
/agent run test
```

## 📊 Response Types

- **Ephemeral responses** (only you see them): Status checks, help, errors
- **Channel responses** (everyone sees them): Successful agent runs, completion notifications

## 🔍 Troubleshooting

### Common Issues

**1. "Command not found" error:**
- Verify the slash command is created in your Slack app
- Check the Request URL is correct
- Ensure your API is deployed and accessible

**2. "Invalid Slack signature" error:**
- Verify `SLACK_SIGNING_SECRET` is set correctly
- Check your API logs for the exact error
- Test with signature verification disabled first

**3. Commands work but agent doesn't run:**
- Check your API logs for errors
- Verify `OPENAI_API_KEY` is set
- Ensure `config.json` is accessible
- Test the `/run` endpoint directly via curl

**4. Slash command takes too long:**
- Slack has a 3-second timeout for slash commands
- Our implementation uses background tasks to handle this
- The initial response is immediate, agent runs in background

### Debug Steps

1. **Check API health:**
   ```bash
   curl https://your-api.com/health
   ```

2. **Test direct API call:**
   ```bash
   curl -X POST "https://your-api.com/run" \
     -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"force": true, "dry_run": true}'
   ```

3. **Check API logs:**
   - Render: View in dashboard
   - Fly.io: `fly logs`
   - Docker: `docker-compose logs -f`

## 🔐 Security Best Practices

1. **Always set a strong API_KEY**
2. **Use SLACK_SIGNING_SECRET for production**
3. **Limit Slack app permissions to minimum required**
4. **Monitor API access logs**
5. **Regularly rotate secrets**
6. **Consider IP whitelisting if possible**

## 📈 Monitoring & Notifications

### Set Up Slack Notifications

Your agent can post completion notifications back to Slack. Update your agent's notification configuration to include Slack webhooks.

### Usage Analytics

Monitor slash command usage in your API logs to understand:
- Who is triggering the agent most
- Peak usage times
- Common failure points

## 🚀 Next Steps

Once Slack integration is working:

1. **Train your team** on the available commands
2. **Set up scheduled runs** using `/agent run force` in automated workflows
3. **Create custom shortcuts** for common use cases
4. **Monitor usage** and optimize based on team feedback
5. **Consider adding more interactive elements** like buttons for common actions

Your AI agent is now fully integrated with Slack! 🎉