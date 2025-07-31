#!/usr/bin/env python3
"""
Simple test API for Azure deployment debugging
"""

import os
from datetime import datetime

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError:
    print("FastAPI not installed, installing...")
    os.system("pip install fastapi uvicorn")
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Simple Test API",
    description="Basic API to test Azure deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Basic health check"""
    return {
        "message": "🎉 Aircall Agent API is working!",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running successfully on Azure!"
    }

@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working!",
        "environment": {
            "PORT": os.getenv("PORT", "not set"),
            "HOST": os.getenv("HOST", "not set"),
            "PYTHON_VERSION": os.sys.version,
        }
    }

if __name__ == "__main__":
    # Get host and port from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Simple Test API on {host}:{port}")
    print("✅ Environment check passed")
    
    # Run the server
    uvicorn.run(app, host=host, port=port, log_level="info")