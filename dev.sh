#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}"
echo "================================"
echo "🚀 ScribeEasy Development Server"
echo "================================"
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if command_exists python3; then
    PYTHON_CMD="python3"
elif command_exists python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found. Please install Python 3.8+ and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found: $PYTHON_CMD${NC}"

# Check if Node.js is installed
if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

# Check if npm is installed
if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install npm and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm found${NC}"

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}❌ Frontend dependencies not installed.${NC}"
    echo -e "${YELLOW}Please run: cd frontend && npm install${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Check if backend dependencies are installed
cd backend
if ! $PYTHON_CMD -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    echo -e "${RED}❌ Backend dependencies not installed.${NC}"
    echo -e "${YELLOW}Please run: cd backend && pip install -r requirements.txt${NC}"
    cd ..
    exit 1
fi
cd ..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

echo ""
echo -e "${CYAN}Starting development servers...${NC}"
echo -e "${CYAN}Backend will be available at: http://localhost:8000${NC}"
echo -e "${CYAN}Frontend will be available at: http://localhost:5173${NC}"
echo -e "${CYAN}API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend server
echo -e "${BLUE}[BACKEND] Starting backend server...${NC}"
cd backend
$PYTHON_CMD -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo -e "${GREEN}[FRONTEND] Starting frontend server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
