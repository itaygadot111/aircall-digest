#!/bin/bash

# Azure App Service startup script for AI Competitive Intelligence Agent

echo "Starting Aircall Intelligence Agent API..."

# Set default values if environment variables are not set
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-"8000"}

echo "Host: $HOST, Port: $PORT"

# Check if required files exist
if [ ! -f "config.json" ]; then
    echo "ERROR: config.json not found"
    exit 1
fi

if [ ! -f "api.py" ]; then
    echo "ERROR: api.py not found"
    exit 1
fi

# Test imports
echo "Testing Python imports..."
python -c "
try:
    import fastapi
    import uvicorn  
    import httpx
    print('✅ All required modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

# Start the application
echo "Starting FastAPI application..."
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind $HOST:$PORT --timeout 120 --preload api:app