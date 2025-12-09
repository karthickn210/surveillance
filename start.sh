#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping Surveillance System..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup SIGINT

echo "Starting Backend..."
cd backend
# Check for venv and use it
if [ -d ".venv" ]; then
    echo "Using virtual environment..."
    source .venv/bin/activate
fi
# pip install -r requirements.txt # Uncomment if dependencies not installed
python main.py &
BACKEND_PID=$!
cd ..

echo "Starting Frontend..."
cd frontend
# npm install # Uncomment if dependencies not installed
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo "System Running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"

wait
