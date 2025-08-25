#!/bin/bash

# Proposal Master Development Startup Script
# This script starts both the backend API and frontend development servers

echo "🚀 Starting Proposal Master Development Environment"
echo "================================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   ✅ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✅ Frontend server stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Start the backend API server
echo "🔧 Starting backend API server..."
cd "$(dirname "$0")"
uvicorn simple_dev_api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   ✅ Backend server started (PID: $BACKEND_PID)"
echo "   🌐 API available at: http://localhost:8000"

# Wait a moment for the backend to start
sleep 2

# Start the frontend development server
echo "🔧 Starting frontend development server..."
cd Frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "   📦 Installing frontend dependencies..."
    npm install
fi

# Start the frontend server
npm run dev &
FRONTEND_PID=$!
echo "   ✅ Frontend server started (PID: $FRONTEND_PID)"
echo "   🌐 Frontend available at: http://localhost:5173"

echo ""
echo "🎉 Development environment ready!"
echo "================================================="
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "Health:   http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for background processes
wait
