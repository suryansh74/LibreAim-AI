#!/bin/bash
# Run LibreAim AI

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Try to allow display access
xhost +local: 2>/dev/null || true

source venv/bin/activate
python aim_ai.py
