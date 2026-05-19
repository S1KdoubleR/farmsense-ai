#!/bin/bash
# run.sh — FarmSense AI
# Starts both the backend (FastAPI) and frontend (Vite) concurrently.
# Usage: chmod +x run.sh && ./run.sh
# Windows users: run backend and frontend in separate terminals.

echo ""
echo "╔══════════════════════════════════════╗"
echo "║        🌿  FarmSense AI              ║"
echo "║   Intelligent Crop Recommendation    ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check if dataset exists
if [ ! -f "backend/data/crop_data.csv" ]; then
  echo "⚠️  WARNING: Dataset not found at backend/data/crop_data.csv"
  echo "   Download from: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset"
  echo "   Rename to crop_data.csv and place in backend/data/"
  echo ""
fi

echo "🚀 Starting backend on http://localhost:8001 ..."
cd backend && uvicorn main:app --reload --port 8001 &
BACKEND_PID=$!

echo "🌐 Starting frontend on http://localhost:5173 ..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both services started!"
echo "   Backend  -> http://localhost:8001"
echo "   Frontend -> http://localhost:5173"
echo "   API Docs -> http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both services."
echo ""

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID
