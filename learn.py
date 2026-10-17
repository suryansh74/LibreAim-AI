#!/usr/bin/env python3
"""
Learn from gameplay - improved capture.
"""

import cv2
import numpy as np
import mss
import time
import json
import subprocess
import os
from pynput import mouse

PARAMS_FILE = "learned_params.json"

class GameplayLearner:
    def __init__(self):
        self.sct = mss.MSS()
        self.samples = []
        self.click_count = 0
        self.running = True
        self.last_click_time = 0
        self.use_scrot = self._check_scrot()
        
    def _check_scrot(self):
        try:
            subprocess.run(["scrot", "--version"], capture_output=True, check=False)
            return True
        except FileNotFoundError:
            return False
    
    def get_screen(self):
        """Capture screen. Try scrot first (better with OpenGL), fall back to mss."""
        if self.use_scrot:
            try:
                path = "/tmp/aim_capture.png"
                subprocess.run(["scrot", "-o", path], capture_output=True, check=True, timeout=2)
                img = cv2.imread(path)
                if img is not None and img.mean() > 5:  # not black
                    monitor = self.sct.monitors[1]
                    return img, monitor
            except Exception:
                pass
        
        # Fallback to mss
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def on_click(self, x, y, button, pressed):
        if not pressed or button != mouse.Button.left:
            return
        
        now = time.time()
        if now - self.last_click_time < 0.2:
            return
        self.last_click_time = now
        
        try:
            img, monitor = self.get_screen()
            ix = x - monitor["left"]
            iy = y - monitor["top"]
            
            h, w = img.shape[:2]
            if not (0 <= ix < w and 0 <= iy < h):
                return
            
            # Sample larger region
            r = 15
            x1, y1 = max(0, ix - r), max(0, iy - r)
            x2, y2 = min(w, ix + r), min(h, iy + r)
            region = img[y1:y2, x1:x2]
            
            if region.size == 0:
                return
            
            avg_bgr = region.mean(axis=(0, 1))
            
            # Skip near-black samples (capture failed)
            if avg_bgr.mean() < 15:
                print(f"  (ignored black sample at {ix}, {iy})")
                return
            
            hsv = cv2.cvtColor(np.uint8([[avg_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
            
            self.samples.append({
                "bgr": avg_bgr.tolist(),
                "hsv": hsv.tolist(),
                "x": int(ix),
                "y": int(iy)
            })
            self.click_count += 1
            print(f"Learned #{self.click_count} | HSV={hsv} | BGR={avg_bgr.astype(int)} | pos=({ix}, {iy})")
            
        except Exception as e:
            print(f"Error: {e}")
    
    def save_params(self):
        if len(self.samples) < 8:
            print(f"\nOnly {len(self.samples)} valid samples. Need more (click targets, not empty space).")
            return False
        
        hsvs = np.array([s["hsv"] for s in self.samples])
        
        lower = np.percentile(hsvs, 5, axis=0)
        upper = np.percentile(hsvs, 95, axis=0)
        
        margin = np.array([10, 50, 50])
        lower = np.clip(lower - margin, [0, 0, 0], [180, 255, 255])
        upper = np.clip(upper + margin, [0, 0, 0], [180, 255, 255])
        
        params = {
            "lower_hsv": lower.tolist(),
            "upper_hsv": upper.tolist(),
            "sample_count": len(self.samples),
            "avg_hsv": hsvs.mean(axis=0).tolist(),
            "timestamp": time.time()
        }
        
        with open(PARAMS_FILE, "w") as f:
            json.dump(params, f, indent=2)
        
        print(f"\nSaved {len(self.samples)} samples to {PARAMS_FILE}")
        print(f"HSV range: {lower.astype(int)} -> {upper.astype(int)}")
        return True
    
    def run(self):
        print("=" * 50)
        print("GAMEPLAY LEARNING MODE")
        print("=" * 50)
        if self.use_scrot:
            print("Using scrot for capture (better with OpenGL games)")
        else:
            print("scrot not found. Install it for better results: sudo apt install scrot")
            print("Using mss fallback.")
        print()
        print("1. Start LibreAim, begin a scenario")
        print("2. Click the yellow targets (not empty space)")
        print("3. Get at least 15-20 good clicks")
        print("4. Press Ctrl+C when done")
        print()
        
        listener = mouse.Listener(on_click=self.on_click)
        listener.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            listener.stop()
            self.save_params()
            print("\nNow run: ./run.sh")

def main():
    GameplayLearner().run()

if __name__ == "__main__":
    main()
