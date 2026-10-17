#!/usr/bin/env python3
"""
Learn from gameplay.
Run this, play LibreAim normally, click targets.
It records the colors you click and builds detection parameters.
"""

import cv2
import numpy as np
import pyautogui
import mss
import time
import json
import os
from pynput import mouse

# File where learned parameters are saved
PARAMS_FILE = "learned_params.json"

class GameplayLearner:
    def __init__(self):
        self.sct = mss.MSS()
        self.samples = []
        self.click_count = 0
        self.running = True
        self.last_click_time = 0
        
    def get_screen(self):
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def on_click(self, x, y, button, pressed):
        if not pressed or button != mouse.Button.left:
            return
        
        # Debounce
        now = time.time()
        if now - self.last_click_time < 0.15:
            return
        self.last_click_time = now
        
        try:
            img, monitor = self.get_screen()
            # Convert screen coords to image coords
            ix = x - monitor["left"]
            iy = y - monitor["top"]
            
            h, w = img.shape[:2]
            if 0 <= ix < w and 0 <= iy < h:
                # Sample a small region around the click
                r = 8
                x1, y1 = max(0, ix - r), max(0, iy - r)
                x2, y2 = min(w, ix + r), min(h, iy + r)
                region = img[y1:y2, x1:x2]
                
                if region.size > 0:
                    # Get average color in the region
                    avg_bgr = region.mean(axis=(0, 1))
                    hsv = cv2.cvtColor(np.uint8([[avg_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                    
                    self.samples.append({
                        "bgr": avg_bgr.tolist(),
                        "hsv": hsv.tolist(),
                        "x": int(ix),
                        "y": int(iy)
                    })
                    self.click_count += 1
                    print(f"Learned click #{self.click_count} | HSV={hsv} | pos=({ix}, {iy})")
        except Exception as e:
            print(f"Sample error: {e}")
    
    def save_params(self):
        if len(self.samples) < 5:
            print(f"\nNot enough samples ({len(self.samples)}). Click more targets.")
            return False
        
        hsvs = np.array([s["hsv"] for s in self.samples])
        
        # Compute robust range (percentile to ignore outliers)
        lower = np.percentile(hsvs, 10, axis=0)
        upper = np.percentile(hsvs, 90, axis=0)
        
        # Add some margin
        margin = np.array([8, 40, 40])
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
        
        print(f"\nSaved parameters from {len(self.samples)} clicks to {PARAMS_FILE}")
        print(f"Lower HSV: {lower}")
        print(f"Upper HSV: {upper}")
        return True
    
    def run(self):
        print("=" * 50)
        print("GAMEPLAY LEARNING MODE")
        print("=" * 50)
        print("1. Start LibreAim and begin a scenario")
        print("2. Play normally — click the targets")
        print("3. Click at least 20-30 targets")
        print("4. Press Ctrl+C here when done")
        print()
        print("Listening for your clicks...")
        print()
        
        listener = mouse.Listener(on_click=self.on_click)
        listener.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nStopping learning...")
        finally:
            listener.stop()
            self.save_params()
            print("\nDone. Now you can run the AI with: ./run.sh")

def main():
    learner = GameplayLearner()
    learner.run()

if __name__ == "__main__":
    main()
