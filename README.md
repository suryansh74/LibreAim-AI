# Aim Trainer AI (External Computer Vision Bot)

A Python AI that looks at your screen, detects targets in LibreAim (or other aim trainers), and automatically aims + clicks.

## Requirements

- Python 3.8+
- Linux
- LibreAim running and visible (windowed mode recommended)

## Quick Start (with venv)

```bash
# 1. Make scripts executable
chmod +x setup.sh run.sh

# 2. Create virtual environment and install dependencies
./setup.sh

# 3. Start LibreAim (windowed mode)

# 4. Run the AI
./run.sh
```

## Manual venv method

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python aim_ai.py
```

## Controls

- **To stop**: Move mouse to the **top-left corner** of the screen, or press `Ctrl+C`.

## Tips for LibreAim

- Run LibreAim in **windowed mode** for better detection.
- Choose option **1** (red targets) when the AI starts.
- If detection is poor, edit the color ranges or size limits at the top of `aim_ai.py`.

## License

MIT
