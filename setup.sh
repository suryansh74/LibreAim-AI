#!/bin/bash
# Setup for LibreAim AI

echo "Creating virtual environment..."
python3 -m venv venv

echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Before running, allow display access:"
echo "  xhost +local:"
echo ""
echo "Then run:"
echo "  ./run.sh"
