#!/bin/bash

echo "🧪 Testing Proposal Master Development Environment"
echo "================================================="

# Start the development environment in background
echo "🚀 Starting development servers..."
./start_dev.sh &
DEV_PID=$!

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 8

echo ""
echo "🔍 Testing Backend API..."
echo "-------------------------"

# Test health endpoint
echo "Testing /health endpoint:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ Health endpoint failed"

echo ""
echo "Testing /documents endpoint:"
curl -s http://localhost:8000/documents | python3 -m json.tool || echo "❌ Documents endpoint failed"

echo ""
echo "Testing /proposals endpoint:"
curl -s http://localhost:8000/proposals | python3 -m json.tool || echo "❌ Proposals endpoint failed"

echo ""
echo "🌐 Testing Frontend..."
echo "---------------------"
echo "Frontend should be available at:"
echo "  - http://localhost:3000 (primary)"
echo "  - http://localhost:5173 (fallback)"

# Test if frontend is responding
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding on port 3000"
elif curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend is responding on port 5173"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "📊 Summary:"
echo "==========="
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend:     http://localhost:3000 or http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the development environment"

# Wait for the development process
wait $DEV_PID
