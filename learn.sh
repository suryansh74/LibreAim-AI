#!/bin/bash
# Learn from your gameplay

if [ ! -d "venv" ]; then
    echo "Run ./setup.sh first"
    exit 1
fi

xhost +local: 2>/dev/null || true
source venv/bin/activate
python learn.py
