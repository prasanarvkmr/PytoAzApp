#!/bin/bash

# Startup script for running both FastAPI and Streamlit on Azure App Service

cd /home/site/wwwroot

# Set Python path to include installed packages
export PYTHONPATH="/home/site/wwwroot/.python_packages/lib/site-packages:/home/site/wwwroot/antenv/lib/python3.11/site-packages:${PYTHONPATH}"

# Set API URL for Streamlit to connect to FastAPI
export API_URL="http://127.0.0.1:8001"

# Log startup info
echo "=== Starting Application ==="
echo "Working directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"
ls -la

# Start FastAPI in background on port 8001
echo "Starting FastAPI server on port 8001..."
nohup python -m uvicorn api:app --host 127.0.0.1 --port 8001 --log-level info > /tmp/fastapi.log 2>&1 &

# Wait for FastAPI to start
sleep 5

# Verify FastAPI is running
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "FastAPI started successfully"
else
    echo "FastAPI health check failed - check /tmp/fastapi.log"
    cat /tmp/fastapi.log
fi

# Start Streamlit on port 8000 (main port exposed to Azure)
echo "Starting Streamlit server on port 8000..."
python -m streamlit run app.py \
    --server.port=8000 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false