"""
Vercel serverless function for AI Competitive Intelligence Agent
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

# Vercel serverless function imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import hashlib
import hmac

# Initialize FastAPI app
app = FastAPI(
    title="AI Competitive Intelligence Agent API",
    description="REST API for triggering competitive intelligence digests",
    version="1.0.0"
)

# Security
security = HTTPBearer()

class AgentRunRequest(BaseModel):
    """Request model for agent execution"""
    config_file: Optional[str] = "config.json"
    output_file: Optional[str] = None
    dry_run: bool = False
    force: bool = False
    verbose: bool = False

class AgentRunResponse(BaseModel):
    """Response model for agent execution"""
    job_id: str
    status: str
    message: str
    started_at: str

class WebhookPayload(BaseModel):
    """Generic webhook payload"""
    trigger: str
    data: Optional[Dict] = None

# In-memory job storage (use database in production)
jobs: Dict[str, Dict] = {}

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header"""
    api_key = os.getenv("API_KEY")
    if not api_key:
        return True  # No API key configured, allow access
    
    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "name": "AI Competitive Intelligence Agent API",
        "version": "1.0.0",
        "status": "running",
        "platform": "Vercel Serverless",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """Trigger agent execution (simplified for Vercel)"""
    job_id = str(uuid.uuid4())
    
    # For Vercel, we'll simulate the agent run since serverless functions have time limits
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "request": request.dict(),
        "message": "Simulated agent run completed successfully (Vercel demo mode)",
        "output_file": f"digest_{job_id}.html"
    }
    
    return AgentRunResponse(
        job_id=job_id,
        status="completed",
        message="Agent execution completed (demo mode)",
        started_at=jobs[job_id]["started_at"]
    )

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job execution status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    return list(jobs.values())

@app.post("/webhook/trigger")
async def webhook_trigger(payload: WebhookPayload):
    """Generic webhook endpoint for external triggers"""
    
    job_id = str(uuid.uuid4())
    
    # Simulate agent run
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "trigger": payload.trigger,
        "webhook_data": payload.data,
        "message": f"Agent triggered by {payload.trigger} (demo mode)"
    }
    
    return {
        "job_id": job_id,
        "trigger": payload.trigger,
        "status": "completed",
        "message": f"Agent execution triggered by {payload.trigger}",
        "started_at": jobs[job_id]["started_at"]
    }

@app.post("/webhook/zapier")
async def zapier_webhook(request: Request):
    """Zapier-specific webhook endpoint"""
    try:
        payload = await request.json()
    except:
        payload = {}
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "trigger": "zapier",
        "webhook_data": payload,
        "message": "Agent triggered by Zapier (demo mode)"
    }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "message": "Agent execution triggered by Zapier",
        "started_at": jobs[job_id]["started_at"]
    }

# Slack Integration (simplified)
@app.post("/slack/command")
async def slack_slash_command(
    request: Request,
    token: str = Form(...),
    team_id: str = Form(...),
    team_domain: str = Form(...),
    channel_id: str = Form(...),
    channel_name: str = Form(...),
    user_id: str = Form(...),
    user_name: str = Form(...),
    command: str = Form(...),
    text: str = Form(""),
    response_url: str = Form(...),
    trigger_id: str = Form(...)
):
    """Handle Slack slash commands"""
    
    args = text.strip().lower().split() if text.strip() else []
    
    if not args or args[0] == "help":
        return {
            "response_type": "ephemeral",
            "text": "🤖 *Aircall Intelligence Agent Commands*\n\n• `/agent run` - Trigger intelligence digest\n• `/agent status` - Check status\n• `/agent help` - Show this help"
        }
    
    elif args[0] == "run":
        job_id = str(uuid.uuid4())
        
        jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "started_at": datetime.now().isoformat(),
            "trigger": "slack",
            "slack_user": user_name
        }
        
        return {
            "response_type": "in_channel",
            "text": f"🚀 Agent run completed!\n📋 Job ID: `{job_id}`\n👤 Triggered by: @{user_name}"
        }
    
    else:
        return {
            "response_type": "ephemeral",
            "text": f"❓ Unknown command: `{args[0]}`\nUse `/agent help` to see available commands."
        }

# Export the app for Vercel
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel handler
def handler(request, context):
    """Vercel serverless function handler"""
    return app(request, context)