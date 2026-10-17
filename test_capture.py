#!/usr/bin/env python3
"""
Test which screen capture method can see LibreAim.
Run this while LibreAim is open with targets visible.
"""

import subprocess
import os
import time

def test_capture(name, cmd, outfile):
    print(f"\nTesting: {name}")
    print(f"  Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        if os.path.exists(outfile) and os.path.getsize(outfile) > 1000:
            print(f"  SUCCESS -> {outfile} ({os.path.getsize(outfile)} bytes)")
            return True
        else:
            print(f"  FAILED (no useful output)")
            if result.stderr:
                print(f"  Error: {result.stderr.decode()[:200]}")
            return False
    except FileNotFoundError:
        print(f"  NOT INSTALLED")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    print("=" * 50)
    print("SCREEN CAPTURE TEST")
    print("=" * 50)
    print("Make sure LibreAim is open with yellow targets visible.")
    print("This will try different capture methods.")
    input("Press Enter when ready...")
    
    methods = [
        ("scrot", ["scrot", "-o", "/tmp/test_scrot.png"], "/tmp/test_scrot.png"),
        ("import (ImageMagick)", ["import", "-window", "root", "/tmp/test_import.png"], "/tmp/test_import.png"),
        ("ffmpeg x11grab", ["ffmpeg", "-y", "-f", "x11grab", "-video_size", "1920x1080", "-i", ":0", "-frames:v", "1", "/tmp/test_ffmpeg.png"], "/tmp/test_ffmpeg.png"),
        ("gnome-screenshot", ["gnome-screenshot", "-f", "/tmp/test_gnome.png"], "/tmp/test_gnome.png"),
    ]
    
    working = []
    for name, cmd, outfile in methods:
        if test_capture(name, cmd, outfile):
            working.append((name, outfile))
    
    print("\n" + "=" * 50)
    if working:
        print("WORKING METHODS:")
        for name, path in working:
            print(f"  - {name}: {path}")
        print("\nOpen the images and check which one actually shows the yellow targets.")
    else:
        print("No capture method worked.")
        print("\nTry these fixes:")
        print("  1. sudo apt install scrot imagemagick ffmpeg")
        print("  2. Run LibreAim with software rendering:")
        print("     LIBGL_ALWAYS_SOFTWARE=1 ./LibreAim-v0.4-linux.x86_64")
        print("  3. Or disable compositor temporarily")

if __name__ == "__main__":
    main()
