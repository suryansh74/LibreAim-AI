# LibreAim AI - Learns from Your Gameplay

A general AI that learns target appearance from your clicks, then plays by itself.

## How it works

1. **Learn mode**: You play normally. Every time you click a target, it records the color.
2. **Play mode**: It uses the colors it learned to find and click targets automatically.

## Setup

```bash
chmod +x setup.sh learn.sh run.sh
./setup.sh
```

## Step 1: Learn from your gameplay

```bash
./learn.sh
```

- Start LibreAim and begin a scenario (Random targets is fine)
- Play normally — click the yellow targets
- Click at least **20–30 targets**
- Press `Ctrl+C` in the terminal when done

It saves what it learned to `learned_params.json`.

## Step 2: Let the AI play

```bash
./run.sh
```

- Start LibreAim and begin a scenario
- The AI will detect targets using the colors it learned from you
- To stop: move mouse to top-left corner or press `Ctrl+C`

## Tips

- The more targets you click during learning, the better it gets
- If targets change color, run `./learn.sh` again
- Works best in windowed mode
- Keep the game window visible and unpaused

## Files

- `learn.py` — records your clicks and builds parameters
- `aim_ai.py` — plays using learned parameters
- `learned_params.json` — created after learning

## License

MIT
