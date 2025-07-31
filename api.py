#!/usr/bin/env python3
"""
REST API wrapper for AI Competitive Intelligence Agent
Enables remote triggering via HTTP requests and webhooks
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import httpx

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import hashlib
import hmac
from urllib.parse import parse_qs

from src.agent import CompetitiveIntelligenceAgent
from src.config import Config
from src.logger import setup_logger

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

class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    output_file: Optional[str] = None
    error: Optional[str] = None

class WebhookPayload(BaseModel):
    """Generic webhook payload"""
    trigger: str
    data: Optional[Dict] = None

class SlackSlashCommandRequest(BaseModel):
    """Slack slash command request"""
    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    response_url: str
    trigger_id: str

# In-memory job storage (use Redis/database in production)
jobs: Dict[str, Dict] = {}

def verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Verify Slack request signature"""
    slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    if not slack_signing_secret:
        return True  # Skip verification if no secret configured
    
    # Create signature
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    my_signature = 'v0=' + hmac.new(
        slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, signature)

def create_slack_response(text: str, response_type: str = "ephemeral", attachments: List[Dict] = None) -> Dict:
    """Create a formatted Slack response"""
    response = {
        "response_type": response_type,
        "text": text
    }
    if attachments:
        response["attachments"] = attachments
    return response

def create_agent_status_attachment(job_id: str, job_data: Dict) -> Dict:
    """Create Slack attachment for agent job status"""
    status = job_data.get("status", "unknown")
    
    color_map = {
        "queued": "#36a64f",
        "running": "#ffa500", 
        "completed": "#36a64f",
        "failed": "#ff0000",
        "skipped": "#808080"
    }
    
    fields = [
        {"title": "Job ID", "value": job_id, "short": True},
        {"title": "Status", "value": status.title(), "short": True},
        {"title": "Started", "value": job_data.get("started_at", "Unknown"), "short": True}
    ]
    
    if job_data.get("completed_at"):
        fields.append({"title": "Completed", "value": job_data["completed_at"], "short": True})
    
    if job_data.get("output_file"):
        fields.append({"title": "Output", "value": job_data["output_file"], "short": False})
    
    if job_data.get("error"):
        fields.append({"title": "Error", "value": job_data["error"], "short": False})
    
    return {
        "color": color_map.get(status, "#808080"),
        "title": "🤖 Agent Execution Status",
        "fields": fields,
        "footer": "Aircall Intelligence Agent",
        "ts": int(datetime.now().timestamp())
    }

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

async def send_slack_notification(job_id: str, job_data: Dict):
    """Send completion notification to Slack"""
    slack_context = job_data.get("slack_context")
    if not slack_context or not slack_context.get("response_url"):
        return
    
    try:
        status = job_data.get("status", "unknown")
        
        if status == "completed":
            text = f"✅ Agent run completed successfully!"
            color = "#36a64f"
        elif status == "failed":
            text = f"❌ Agent run failed"
            color = "#ff0000"
        elif status == "skipped":
            text = f"⏭️ Agent run skipped (recently executed)"
            color = "#808080"
        else:
            return  # Don't notify for other statuses
        
        attachment = create_agent_status_attachment(job_id, job_data)
        attachment["color"] = color
        
        payload = {
            "response_type": "in_channel",
            "text": text,
            "attachments": [attachment]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                slack_context["response_url"],
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")

async def run_agent_task(job_id: str, request: AgentRunRequest):
    """Background task to run the agent"""
    try:
        jobs[job_id]["status"] = "running"
        
        # Setup logging
        logger = setup_logger(verbose=request.verbose)
        
        # Load configuration
        config = Config.from_file(request.config_file)
        
        # Initialize agent
        agent = CompetitiveIntelligenceAgent(config, logger, verbose=request.verbose)
        
        # Check if we should run
        if not request.force and not agent.should_run():
            jobs[job_id]["status"] = "skipped"
            jobs[job_id]["message"] = "Agent was recently executed. Use force=true to override."
            jobs[job_id]["completed_at"] = datetime.now().isoformat()
            
            # Send Slack notification
            await send_slack_notification(job_id, jobs[job_id])
            return
        
        # Determine output file
        output_file = request.output_file or f"digest_{job_id}.html"
        
        # Run the agent
        logger.info(f"Starting agent run for job {job_id}")
        digest = await agent.run()
        
        # Save digest
        agent.save_digest(digest, output_file)
        
        # Send notifications if not dry run
        if not request.dry_run:
            agent.send_notifications(digest)
        
        # Update job status
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_file"] = output_file
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        jobs[job_id]["message"] = f"Agent completed successfully. Digest saved to {output_file}"
        
        logger.info(f"Agent run {job_id} completed successfully")
        
        # Send Slack notification
        await send_slack_notification(job_id, jobs[job_id])
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        logger.error(f"Agent run {job_id} failed: {str(e)}")
        
        # Send Slack notification
        await send_slack_notification(job_id, jobs[job_id])

@app.get("/", response_model=Dict)
async def root():
    """API health check and info"""
    return {
        "name": "AI Competitive Intelligence Agent API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/run", response_model=AgentRunResponse, dependencies=[Depends(verify_api_key)])
async def run_agent(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """Trigger agent execution"""
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "started_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    # Add background task
    background_tasks.add_task(run_agent_task, job_id, request)
    
    return AgentRunResponse(
        job_id=job_id,
        status="queued",
        message="Agent execution queued",
        started_at=jobs[job_id]["started_at"]
    )

@app.get("/jobs/{job_id}", response_model=JobStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_job_status(job_id: str):
    """Get job execution status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatusResponse(**job)

@app.get("/jobs", response_model=List[JobStatusResponse], dependencies=[Depends(verify_api_key)])
async def list_jobs():
    """List all jobs"""
    return [JobStatusResponse(**job) for job in jobs.values()]

@app.get("/output/{filename}", dependencies=[Depends(verify_api_key)])
async def download_output(filename: str):
    """Download generated digest file"""
    file_path = Path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/html" if filename.endswith(".html") else "application/octet-stream"
    )

@app.post("/webhook/trigger", dependencies=[Depends(verify_api_key)])
async def webhook_trigger(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Generic webhook endpoint for external triggers"""
    
    # Map different triggers to agent configurations
    trigger_configs = {
        "daily": AgentRunRequest(force=False, dry_run=False),
        "weekly": AgentRunRequest(force=True, dry_run=False),
        "test": AgentRunRequest(force=True, dry_run=True, verbose=True)
    }
    
    if payload.trigger not in trigger_configs:
        raise HTTPException(status_code=400, detail=f"Unknown trigger: {payload.trigger}")
    
    request = trigger_configs[payload.trigger]
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "started_at": datetime.now().isoformat(),
        "request": request.dict(),
        "trigger": payload.trigger,
        "webhook_data": payload.data
    }
    
    # Add background task
    background_tasks.add_task(run_agent_task, job_id, request)
    
    return {
        "job_id": job_id,
        "trigger": payload.trigger,
        "status": "queued",
        "message": f"Agent execution triggered by {payload.trigger}",
        "started_at": jobs[job_id]["started_at"]
    }

@app.post("/webhook/zapier", dependencies=[Depends(verify_api_key)])
async def zapier_webhook(request: Request, background_tasks: BackgroundTasks):
    """Zapier-specific webhook endpoint"""
    try:
        payload = await request.json()
    except:
        payload = {}
    
    # Create agent run request
    agent_request = AgentRunRequest(
        force=payload.get("force", False),
        dry_run=payload.get("dry_run", False),
        verbose=payload.get("verbose", False)
    )
    
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "started_at": datetime.now().isoformat(),
        "request": agent_request.dict(),
        "trigger": "zapier",
        "webhook_data": payload
    }
    
    # Add background task
    background_tasks.add_task(run_agent_task, job_id, agent_request)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Agent execution triggered by Zapier",
        "started_at": jobs[job_id]["started_at"]
    }

@app.delete("/jobs/{job_id}", dependencies=[Depends(verify_api_key)])
async def delete_job(job_id: str):
    """Delete job record"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up output file if it exists
    job = jobs[job_id]
    if job.get("output_file") and Path(job["output_file"]).exists():
        Path(job["output_file"]).unlink()
    
    del jobs[job_id]
    return {"message": f"Job {job_id} deleted"}

# Slack Integration Endpoints

@app.post("/slack/command")
async def slack_slash_command(
    request: Request,
    background_tasks: BackgroundTasks,
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
    
    # Verify Slack signature if configured
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    
    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
    
    # Parse command text
    args = text.strip().lower().split() if text.strip() else []
    
    if not args or args[0] == "help":
        return create_slack_response(
            "🤖 *Aircall Intelligence Agent Commands*\n\n"
            "• `/agent run` - Trigger intelligence digest\n"
            "• `/agent run force` - Force run even if recent\n"
            "• `/agent run test` - Dry run (no notifications)\n" 
            "• `/agent status [job_id]` - Check job status\n"
            "• `/agent jobs` - List recent jobs\n"
            "• `/agent help` - Show this help"
        )
    
    elif args[0] == "run":
        # Parse run options
        force = "force" in args
        dry_run = "test" in args or "dry" in args
        verbose = "verbose" in args or "debug" in args
        
        # Create agent run request
        agent_request = AgentRunRequest(
            force=force,
            dry_run=dry_run,
            verbose=verbose
        )
        
        job_id = str(uuid.uuid4())
        
        # Initialize job with Slack context
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "started_at": datetime.now().isoformat(),
            "request": agent_request.dict(),
            "trigger": "slack",
            "slack_context": {
                "user_id": user_id,
                "user_name": user_name,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "response_url": response_url
            }
        }
        
        # Add background task
        background_tasks.add_task(run_agent_task, job_id, agent_request)
        
        run_type = "🧪 Test run" if dry_run else "🚀 Live run"
        force_text = " (forced)" if force else ""
        
        return create_slack_response(
            f"{run_type} started{force_text}!\n\n"
            f"📋 Job ID: `{job_id}`\n"
            f"👤 Triggered by: @{user_name}\n"
            f"📡 Check status: `/agent status {job_id}`",
            response_type="in_channel"
        )
    
    elif args[0] == "status":
        if len(args) < 2:
            # Show recent jobs for this user
            user_jobs = [
                (job_id, job) for job_id, job in jobs.items()
                if job.get("slack_context", {}).get("user_id") == user_id
            ]
            user_jobs.sort(key=lambda x: x[1]["started_at"], reverse=True)
            
            if not user_jobs:
                return create_slack_response("No recent jobs found for your user.")
            
            recent_jobs = user_jobs[:5]  # Show last 5 jobs
            job_list = "\n".join([
                f"• `{job_id[:8]}...` - {job['status']} ({job['started_at'][:16]})"
                for job_id, job in recent_jobs
            ])
            
            return create_slack_response(
                f"📋 *Your Recent Agent Jobs*\n\n{job_list}\n\n"
                f"Use `/agent status [job_id]` for details"
            )
        
        job_id = args[1]
        # Try to match partial job IDs
        matching_jobs = [jid for jid in jobs.keys() if jid.startswith(job_id)]
        
        if not matching_jobs:
            return create_slack_response(f"❌ Job `{job_id}` not found.")
        
        if len(matching_jobs) > 1:
            return create_slack_response(f"🤔 Multiple jobs match `{job_id}`. Be more specific.")
        
        job_id = matching_jobs[0]
        job_data = jobs[job_id]
        
        attachment = create_agent_status_attachment(job_id, job_data)
        return create_slack_response("", attachments=[attachment])
    
    elif args[0] == "jobs":
        # Show all recent jobs
        recent_jobs = sorted(jobs.items(), key=lambda x: x[1]["started_at"], reverse=True)[:10]
        
        if not recent_jobs:
            return create_slack_response("📭 No recent jobs found.")
        
        job_list = "\n".join([
            f"• `{job_id[:8]}...` - {job['status']} - {job.get('slack_context', {}).get('user_name', 'API')} ({job['started_at'][:16]})"
            for job_id, job in recent_jobs
        ])
        
        return create_slack_response(
            f"📋 *Recent Agent Jobs*\n\n{job_list}\n\n"
            f"Use `/agent status [job_id]` for details"
        )
    
    else:
        return create_slack_response(
            f"❓ Unknown command: `{args[0]}`\n"
            f"Use `/agent help` to see available commands."
        )

@app.post("/slack/interactive")
async def slack_interactive_component(request: Request, background_tasks: BackgroundTasks):
    """Handle Slack interactive components (buttons, etc.)"""
    
    # Verify Slack signature if configured
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    
    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
    
    # Parse form data
    form_data = await request.form()
    payload = json.loads(form_data.get("payload", "{}"))
    
    action = payload.get("actions", [{}])[0]
    action_id = action.get("action_id", "")
    value = action.get("value", "")
    
    user = payload.get("user", {})
    user_name = user.get("name", "unknown")
    user_id = user.get("id", "")
    
    if action_id == "run_agent":
        # Parse action value for options
        options = value.split(",") if value else []
        force = "force" in options
        dry_run = "test" in options
        
        # Create agent run request
        agent_request = AgentRunRequest(force=force, dry_run=dry_run)
        job_id = str(uuid.uuid4())
        
        # Initialize job
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued", 
            "started_at": datetime.now().isoformat(),
            "request": agent_request.dict(),
            "trigger": "slack_button",
            "slack_context": {
                "user_id": user_id,
                "user_name": user_name
            }
        }
        
        # Add background task
        background_tasks.add_task(run_agent_task, job_id, agent_request)
        
        run_type = "🧪 Test run" if dry_run else "🚀 Live run"
        
        return {
            "response_type": "in_channel",
            "text": f"{run_type} started by @{user_name}!",
            "attachments": [{
                "color": "#36a64f",
                "fields": [
                    {"title": "Job ID", "value": job_id, "short": True},
                    {"title": "Status", "value": "Queued", "short": True}
                ]
            }]
        }
    
    elif action_id == "check_status":
        job_id = value
        if job_id in jobs:
            attachment = create_agent_status_attachment(job_id, jobs[job_id])
            return {"response_type": "ephemeral", "attachments": [attachment]}
        else:
            return {"response_type": "ephemeral", "text": f"❌ Job `{job_id}` not found."}
    
    return {"response_type": "ephemeral", "text": "❓ Unknown action."}

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting AI Competitive Intelligence Agent API on {host}:{port}")
    if os.getenv("API_KEY"):
        print("API key authentication enabled")
    else:
        print("WARNING: No API key configured - API is open to all requests")
    
    uvicorn.run(app, host=host, port=port)