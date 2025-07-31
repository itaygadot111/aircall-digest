# GitHub Actions Deployment Guide

This guide shows you how to deploy your AI agent automatically using GitHub Actions whenever you push code to your repository.

## 🚀 **How It Works**

1. **Push code** to your `main` branch
2. **GitHub Actions** automatically runs tests
3. **Deploys** to your chosen cloud provider
4. **Your API** is live and ready to use!

## ⚙️ **Setup Steps**

### Step 1: Choose Your Cloud Provider

Pick one of these options:

#### Option A: Render.com (Easiest)
- ✅ Great for beginners
- ✅ Automatic SSL certificates
- ✅ Simple setup
- 💰 $7/month

#### Option B: Fly.io (Best Value)
- ✅ Excellent performance
- ✅ Global edge deployment
- ✅ Pay-per-use pricing
- 💰 ~$2-5/month

#### Option C: Railway
- ✅ Simple developer experience
- ✅ Good free tier
- 💰 $5/month

## 🔧 **Render.com Setup**

### 1. Create Render Service
1. Go to [render.com](https://render.com) and sign up
2. Click **"New" → "Web Service"**
3. Connect your GitHub repository: `itaygadot111/aircall-digest`
4. Configure:
   - **Name:** `aircall-agent-api`
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Auto-Deploy:** `Yes`

### 2. Set Render Environment Variables
In your Render service dashboard, add:
```
API_KEY=your-secure-api-key-here
OPENAI_API_KEY=your-openai-api-key
TWITTER_BEARER_TOKEN=your-twitter-token
SLACK_SIGNING_SECRET=your-slack-secret
```

### 3. Get Render API Credentials
1. Go to **Account Settings → API Keys**
2. Create a new API key
3. Copy your **Service ID** from the service URL

### 4. Add GitHub Secrets
In your GitHub repository:
1. Go to **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"** and add:

```
RENDER_API_KEY=rnd_xxxxxxxxxxxxx
RENDER_SERVICE_ID=srv-xxxxxxxxxxxxx  
RENDER_SERVICE_NAME=aircall-agent-api
```

## 🛩️ **Fly.io Setup**

### 1. Create Fly.io Account
1. Go to [fly.io](https://fly.io) and sign up
2. Install Fly CLI locally:
   ```bash
   # Mac
   brew install flyctl
   
   # Other platforms
   curl -L https://fly.io/install.sh | sh
   ```

### 2. Login and Initialize
```bash
fly auth login
fly launch --config fly.toml --no-deploy
```

### 3. Get API Token
```bash
fly auth token
```

### 4. Add GitHub Secret
In your GitHub repository secrets:
```
FLY_API_TOKEN=your-fly-api-token-here
```

## 🚂 **Railway Setup**

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app) and sign up
2. Create a new project from your GitHub repository

### 2. Get Railway Token
1. Go to **Account Settings → Tokens**
2. Create a new token
3. Copy your **Service ID** from the project settings

### 3. Add GitHub Secrets
```
RAILWAY_TOKEN=your-railway-token-here
RAILWAY_SERVICE_ID=your-service-id-here
```

## 🔒 **Environment Variables Setup**

Your deployed app needs these environment variables set in the cloud provider dashboard:

### Required
```bash
API_KEY=your-secure-api-key-here
OPENAI_API_KEY=your-openai-api-key
```

### Optional
```bash
TWITTER_BEARER_TOKEN=your-twitter-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
```

## 🧪 **Testing the Setup**

### 1. Commit and Push Your Changes
```bash
git add .
git commit -m "Add GitHub Actions deployment workflows"
git push origin main
```

### 2. Watch the Deployment
1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Watch the **"Test and Deploy"** workflow run

### 3. Check Your API
Once deployed, test your API:
```bash
# Replace with your actual URL
curl https://your-app-name.onrender.com/health
curl https://your-app-name.fly.dev/health
curl https://your-app-name.up.railway.app/health
```

## 📋 **Available Workflows**

I've created several GitHub Actions workflows:

### `test-and-deploy.yml` (Main Workflow)
- ✅ Runs on every push to `main`
- ✅ Tests your code first
- ✅ Auto-detects which cloud provider to use
- ✅ Deploys automatically

### Individual Provider Workflows
- `deploy-render.yml` - Render.com only
- `deploy-fly.yml` - Fly.io only  
- `deploy-railway.yml` - Railway only

## 🎯 **Manual Deployment**

You can also trigger deployments manually:

1. Go to **Actions** tab in your GitHub repository
2. Select the workflow you want to run
3. Click **"Run workflow"**
4. Choose your branch and click **"Run workflow"**

## 🔍 **Troubleshooting**

### Common Issues

**1. "Secret not found" error:**
- Check that you've added all required secrets in GitHub
- Verify secret names match exactly (case-sensitive)

**2. "Build failed" error:**
- Check the Actions logs for specific error messages
- Ensure your `requirements.txt` includes all dependencies
- Verify your `Dockerfile` is correct

**3. "Deployment failed" error:**
- Check your cloud provider dashboard for logs
- Verify API keys and service IDs are correct
- Ensure environment variables are set in the cloud provider

**4. "Health check failed" error:**
- The app might still be starting up (wait 1-2 minutes)
- Check if `config.json` is accessible
- Verify environment variables are set correctly

### Debug Steps

1. **Check GitHub Actions logs:**
   - Go to Actions tab → Click on the failed workflow
   - Expand each step to see detailed logs

2. **Check cloud provider logs:**
   - Render: Service dashboard → Logs
   - Fly.io: `fly logs` command
   - Railway: Project dashboard → Deployments → Logs

3. **Test locally:**
   ```bash
   # Test that your API starts locally
   python api.py
   ```

## 🎉 **Success!**

Once setup is complete:

✅ **Automatic deployments** on every push  
✅ **Testing** before deployment  
✅ **Live API** ready for Slack integration  
✅ **Webhook endpoints** ready for workflow tools  

## 🔄 **Next Steps**

1. **Set up Slack integration** using `SLACK_SETUP.md`
2. **Configure workflow tools** (Zapier, Make.com) with your API URL
3. **Monitor your deployments** in the Actions tab
4. **Scale your app** as needed in your cloud provider dashboard

Your AI agent now has professional CI/CD deployment! 🚀