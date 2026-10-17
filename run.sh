#!/bin/bash
# Run the AI (uses learned parameters)

if [ ! -d "venv" ]; then
    echo "Run ./setup.sh first"
    exit 1
fi

if [ ! -f "learned_params.json" ]; then
    echo "No learned parameters found."
    echo "First run: ./learn.sh"
    echo "Play for a few minutes, then Ctrl+C"
    exit 1
fi

xhost +local: 2>/dev/null || true
source venv/bin/activate
python aim_ai.py
