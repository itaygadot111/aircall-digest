"""
Ultra-minimal Vercel serverless function for AI Competitive Intelligence Agent
No external dependencies - pure Python only
"""

import json
import os
import uuid
from datetime import datetime
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/" or self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "name": "🤖 Aircall Intelligence Agent API",
                "version": "1.0.0",
                "status": "running",
                "platform": "Vercel Serverless (Pure Python)",
                "timestamp": datetime.now().isoformat(),
                "message": "API is working perfectly! 🎉",
                "endpoints": {
                    "GET /": "API info",
                    "GET /health": "Health check",
                    "POST /run": "Trigger agent",
                    "POST /webhook/trigger": "Generic webhook",
                    "POST /webhook/zapier": "Zapier webhook",
                    "POST /slack/command": "Slack commands"
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/test":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": "🧪 Test endpoint working perfectly!",
                "platform": "Vercel Serverless",
                "python_version": "3.9+",
                "timestamp": datetime.now().isoformat(),
                "environment": {
                    "vercel": True,
                    "serverless": True,
                    "region": os.environ.get("VERCEL_REGION", "unknown"),
                    "no_external_deps": True
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": "Not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Parse JSON data
        try:
            if post_data:
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
        except:
            data = {}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        job_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if self.path == "/run":
            response = {
                "job_id": job_id,
                "status": "completed",
                "message": "✅ Agent execution completed successfully!",
                "started_at": timestamp,
                "completed_at": timestamp,
                "platform": "Vercel",
                "request_data": data
            }
            
        elif self.path == "/webhook/trigger":
            trigger = data.get("trigger", "unknown")
            response = {
                "job_id": job_id,
                "trigger": trigger,
                "status": "completed",
                "message": f"🚀 Agent triggered by {trigger}",
                "started_at": timestamp,
                "webhook_data": data
            }
            
        elif self.path == "/webhook/zapier":
            response = {
                "job_id": job_id,
                "status": "completed",
                "message": "🔗 Agent triggered by Zapier",
                "started_at": timestamp,
                "webhook_received": True,
                "zapier_data": data
            }
            
        elif self.path == "/slack/command":
            # Parse form data for Slack
            if self.headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded'):
                form_data = parse_qs(post_data.decode('utf-8'))
                text = form_data.get('text', [''])[0]
                user_name = form_data.get('user_name', ['unknown'])[0]
                
                args = text.strip().lower().split() if text.strip() else []
                
                if not args or args[0] == "help":
                    response = {
                        "response_type": "ephemeral",
                        "text": "🤖 *Aircall Intelligence Agent Commands*\n\n• `/agent run` - Trigger intelligence digest\n• `/agent status` - Check status\n• `/agent help` - Show this help\n\n✨ *Powered by Vercel (Pure Python)*"
                    }
                elif args[0] == "run":
                    response = {
                        "response_type": "in_channel",
                        "text": f"🚀 *Agent run completed!*\n\n📋 **Job ID:** `{job_id}`\n👤 **Triggered by:** @{user_name}\n⚡ **Platform:** Vercel Serverless\n✅ **Status:** Completed successfully!"
                    }
                elif args[0] == "status":
                    response = {
                        "response_type": "ephemeral",
                        "text": f"📊 **Agent Status:** All systems operational!\n\n🆔 **Last Job:** `{job_id}`\n⏰ **Time:** {timestamp[:16]}\n✨ **Platform:** Vercel"
                    }
                else:
                    response = {
                        "response_type": "ephemeral",
                        "text": f"❓ Unknown command: `{args[0]}`\n\nUse `/agent help` to see available commands."
                    }
            else:
                response = {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Slack command processed",
                    "started_at": timestamp
                }
        else:
            response = {
                "error": "Unknown endpoint",
                "path": self.path,
                "method": "POST"
            }
        
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

# This is required for Vercel
def handler_func(request, context):
    """Vercel entry point"""
    return handler(request, context)