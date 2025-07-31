"""
Vercel serverless function for AI Competitive Intelligence Agent
Minimal version for successful deployment
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="AI Competitive Intelligence Agent API",
    description="REST API for triggering competitive intelligence digests",
    version="1.0.0"
)

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

# Simple in-memory job storage
jobs: Dict[str, Dict] = {}

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "name": "🤖 Aircall Intelligence Agent API",
        "version": "1.0.0",
        "status": "running",
        "platform": "Vercel Serverless",
        "timestamp": datetime.now().isoformat(),
        "message": "API is working perfectly! 🎉"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "message": "All systems operational!"
    }

@app.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest):
    """Trigger agent execution (demo mode for Vercel)"""
    job_id = str(uuid.uuid4())
    
    # Simulate agent execution
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "request": request.dict(),
        "message": "✅ Agent execution completed successfully (Vercel demo mode)",
        "output_file": f"digest_{job_id}.html",
        "platform": "Vercel"
    }
    
    return AgentRunResponse(
        job_id=job_id,
        status="completed",
        message="Agent execution completed successfully!",
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
    return {
        "jobs": list(jobs.values()),
        "total": len(jobs),
        "message": f"Found {len(jobs)} jobs"
    }

@app.post("/webhook/trigger")
async def webhook_trigger(payload: WebhookPayload):
    """Generic webhook endpoint for external triggers"""
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "trigger": payload.trigger,
        "webhook_data": payload.data,
        "message": f"🚀 Agent triggered by {payload.trigger}",
        "platform": "Vercel"
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
        payload = {"source": "zapier", "timestamp": datetime.now().isoformat()}
    
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "trigger": "zapier",
        "webhook_data": payload,
        "message": "🔗 Agent triggered by Zapier",
        "platform": "Vercel"
    }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "message": "Agent execution triggered by Zapier",
        "started_at": jobs[job_id]["started_at"],
        "webhook_received": True
    }

@app.post("/slack/command")
async def slack_slash_command(
    token: str = Form(...),
    team_id: str = Form(...),
    channel_id: str = Form(...),
    user_name: str = Form(...),
    command: str = Form(...),
    text: str = Form(""),
    response_url: str = Form(...)
):
    """Handle Slack slash commands"""
    
    args = text.strip().lower().split() if text.strip() else []
    
    if not args or args[0] == "help":
        return {
            "response_type": "ephemeral",
            "text": "🤖 *Aircall Intelligence Agent Commands*\n\n• `/agent run` - Trigger intelligence digest\n• `/agent status` - Check recent jobs\n• `/agent help` - Show this help\n\n✨ *Powered by Vercel*"
        }
    
    elif args[0] == "run":
        job_id = str(uuid.uuid4())
        
        jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "started_at": datetime.now().isoformat(),
            "trigger": "slack",
            "slack_user": user_name,
            "slack_channel": channel_id,
            "platform": "Vercel"
        }
        
        return {
            "response_type": "in_channel",
            "text": f"🚀 *Agent run completed!*\n\n📋 **Job ID:** `{job_id}`\n👤 **Triggered by:** @{user_name}\n⚡ **Platform:** Vercel Serverless\n✅ **Status:** Completed successfully!"
        }
    
    elif args[0] == "status":
        recent_jobs = list(jobs.values())[-5:]  # Last 5 jobs
        if not recent_jobs:
            return {
                "response_type": "ephemeral",
                "text": "📭 No recent jobs found. Try `/agent run` to create one!"
            }
        
        job_list = "\n".join([
            f"• `{job['job_id'][:8]}...` - {job.get('status', 'unknown')} - {job.get('started_at', '')[:16]}"
            for job in recent_jobs
        ])
        
        return {
            "response_type": "ephemeral",
            "text": f"📊 **Recent Jobs:**\n\n{job_list}\n\n✨ Powered by Vercel"
        }
    
    else:
        return {
            "response_type": "ephemeral",
            "text": f"❓ Unknown command: `{args[0]}`\n\nUse `/agent help` to see available commands."
        }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "🧪 Test endpoint working perfectly!",
        "platform": "Vercel Serverless",
        "python_version": "3.11+",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "vercel": True,
            "serverless": True,
            "region": os.getenv("VERCEL_REGION", "unknown")
        }
    }

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This is required for Vercel
def handler(event, context):
    """Vercel serverless function handler"""
    return app(event, context)