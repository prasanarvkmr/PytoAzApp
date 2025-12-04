#!/bin/bash

# Startup script for running both FastAPI and Streamlit on Azure App Service
# This script starts both applications using a process manager approach

cd /home/site/wwwroot

# Set Python path to include installed packages
export PYTHONPATH="/home/site/wwwroot/.python_packages/lib/site-packages:${PYTHONPATH}"

# Set API URL for Streamlit to connect to FastAPI
export API_URL="http://localhost:8001"

# Start FastAPI in background on port 8001
echo "Starting FastAPI server on port 8001..."
python -m uvicorn api:app --host 0.0.0.0 --port 8001 &

# Wait for FastAPI to start
sleep 3

# Start Streamlit on port 8000 (main port exposed to Azure)
echo "Starting Streamlit server on port 8000..."
python -m streamlit run app.py --server.port=8000 --server.address=0.0.0.0 --server.headless=true
