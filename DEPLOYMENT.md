# Remote Deployment Guide

This guide explains how to deploy your AI Competitive Intelligence Agent for remote access via REST API.

## 🚀 Quick Start

### Local Development

1. **Install API dependencies:**
   ```bash
   pip install fastapi uvicorn python-multipart pydantic
   ```

2. **Set API key (optional but recommended):**
   ```bash
   export API_KEY="your-secure-api-key"
   ```

3. **Start the API server:**
   ```bash
   python api.py
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

## 🔗 API Endpoints

### Core Endpoints

- `GET /` - API info and health
- `GET /health` - Health check
- `POST /run` - Trigger agent execution
- `GET /jobs/{job_id}` - Check job status
- `GET /jobs` - List all jobs
- `GET /output/{filename}` - Download digest files

### Webhook Endpoints

- `POST /webhook/trigger` - Generic webhook
- `POST /webhook/zapier` - Zapier-specific webhook

### Example Usage

```bash
# Trigger agent run
curl -X POST "http://localhost:8000/run" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "force": true,
    "dry_run": false,
    "verbose": true
  }'

# Check job status
curl -H "Authorization: Bearer your-api-key" \
  "http://localhost:8000/jobs/job-id-here"

# Webhook trigger
curl -X POST "http://localhost:8000/webhook/trigger" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "daily",
    "data": {"source": "scheduler"}
  }'
```

## 🐳 Docker Deployment

### Local Docker

```bash
# Build image
docker build -t aircall-agent .

# Run container
docker run -p 8000:8000 \
  -e API_KEY="your-api-key" \
  -e OPENAI_API_KEY="your-openai-key" \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/outputs:/app/outputs \
  aircall-agent
```

### Docker Compose

```bash
# Create .env file with your keys
echo "API_KEY=your-secure-api-key" > .env
echo "OPENAI_API_KEY=your-openai-key" >> .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f aircall-agent
```

## ☁️ Cloud Deployment Options

### Option 1: Render.com (Recommended for beginners)

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Use the provided `render.yaml` configuration**
4. **Set environment variables in Render dashboard:**
   - `OPENAI_API_KEY`
   - `API_KEY` (auto-generated or custom)
   - `TWITTER_BEARER_TOKEN` (optional)

**Pros:** Easy setup, automatic deployments, built-in SSL
**Cons:** More expensive than alternatives

### Option 2: Fly.io (Best price/performance)

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and launch:**
   ```bash
   fly auth login
   fly launch --config fly.toml
   ```

3. **Set secrets:**
   ```bash
   fly secrets set OPENAI_API_KEY="your-openai-key"
   fly secrets set API_KEY="your-secure-api-key"
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

**Pros:** Excellent pricing, global edge deployment, good performance
**Cons:** Slightly more complex setup

### Option 3: Railway

1. **Connect GitHub repository to Railway**
2. **Use the provided `railway.json` configuration**
3. **Set environment variables:**
   - `OPENAI_API_KEY`
   - `API_KEY`
   - `TWITTER_BEARER_TOKEN`

**Pros:** Simple deployment, good developer experience
**Cons:** Limited free tier

### Option 4: Google Cloud Run

1. **Build and push to Google Container Registry:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT/aircall-agent
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy aircall-agent \
     --image gcr.io/YOUR_PROJECT/aircall-agent \
     --platform managed \
     --region us-central1 \
     --set-env-vars API_KEY=your-api-key,OPENAI_API_KEY=your-openai-key
   ```

**Pros:** Serverless, pay-per-use, scales to zero
**Cons:** Cold starts, more complex setup

## 🔧 Workflow Tool Integration

### Zapier Integration

1. **Create a Zapier webhook trigger**
2. **Use your deployed API endpoint:**
   ```
   POST https://your-app.render.com/webhook/zapier
   Authorization: Bearer your-api-key
   ```

3. **Zapier will automatically trigger your agent**

### Make.com (Integromat)

1. **Add HTTP module**
2. **Configure POST request to:**
   ```
   https://your-app.render.com/webhook/trigger
   ```
3. **Add headers:**
   ```
   Authorization: Bearer your-api-key
   Content-Type: application/json
   ```
4. **Body:**
   ```json
   {
     "trigger": "daily",
     "data": {"source": "make.com"}
   }
   ```

### GitHub Actions

```yaml
name: Trigger Agent
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM
  workflow_dispatch:

jobs:
  trigger-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Agent
        run: |
          curl -X POST "${{ secrets.AGENT_API_URL }}/run" \
            -H "Authorization: Bearer ${{ secrets.API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"force": true}'
```

### Cron Jobs (Linux/Mac)

```bash
# Add to crontab (crontab -e)
0 9 * * * curl -X POST "https://your-app.render.com/webhook/trigger" -H "Authorization: Bearer your-api-key" -H "Content-Type: application/json" -d '{"trigger":"daily"}'
```

## 🔒 Security Considerations

1. **Always set an API_KEY environment variable**
2. **Use HTTPS in production (automatically handled by cloud providers)**
3. **Store secrets securely using cloud provider secret management**
4. **Consider IP whitelisting for webhook endpoints**
5. **Regularly rotate API keys**
6. **Monitor API access logs**

## 📊 Monitoring & Maintenance

### Health Checks

All cloud providers will automatically monitor the `/health` endpoint.

### Logs

```bash
# Docker Compose
docker-compose logs -f aircall-agent

# Fly.io
fly logs

# Render
# View logs in Render dashboard
```

### Scaling

- **Render/Railway:** Auto-scaling based on traffic
- **Fly.io:** Configure in `fly.toml`
- **Google Cloud Run:** Auto-scales by default

## 🚨 Troubleshooting

### Common Issues

1. **API Key not working:**
   - Ensure `Authorization: Bearer your-api-key` header is set
   - Check environment variables are properly configured

2. **Agent fails to run:**
   - Check OpenAI API key is valid
   - Verify config.json is accessible
   - Check logs for specific error messages

3. **Webhook not triggering:**
   - Verify URL is correct
   - Check Content-Type is `application/json`
   - Ensure proper authentication

4. **Docker build fails:**
   - Ensure all dependencies are in requirements.txt
   - Check Dockerfile syntax
   - Verify base image is accessible

### Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally with Docker
4. Check cloud provider status pages

Your agent is now ready for remote deployment and can be triggered by any workflow tool that supports HTTP webhooks!