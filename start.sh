#!/bin/bash

# ImagineRead Lite - Start Script
# Starts both backend and frontend for local development

echo "🚀 Starting ImagineRead Lite..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Backend
echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Create .env from example if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Start backend in background
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend running on http://localhost:8001${NC}"

# Start Frontend
echo ""
echo -e "${BLUE}🌐 Starting Frontend (Vite)...${NC}"
cd "$SCRIPT_DIR/landing"

# Install deps if needed
if [ ! -d "node_modules" ]; then
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend running on http://localhost:5173${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}🎉 ImagineRead Lite is running!${NC}"
echo "=================================="
echo ""
echo "📱 Landing Page: http://localhost:5173"
echo "📡 API Docs:     http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
