#!/bin/bash

echo "🛑 Stopping any running servers..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
pkill -f "node.*3000" 2>/dev/null
sleep 2

echo "🚀 Starting Backend on port 8000..."
cd /workspaces/Flowmind/backend
python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

echo "⏳ Waiting 5 seconds for backend to start..."
sleep 5

echo "🚀 Starting Frontend on port 3000..."
cd /workspaces/Flowmind/frontend
PORT=3000 BROWSER=none npm start &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Servers started!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 To stop servers: pkill -f uvicorn && pkill -f react-scripts"
echo ""
echo "⏳ Waiting for frontend to compile (30s)..."
sleep 30
echo "✅ Done! Check your browser."
