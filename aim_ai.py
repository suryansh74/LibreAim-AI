#!/usr/bin/env python3
"""
Aim Trainer AI - uses learned parameters.
Improved screen capture.
"""

import cv2
import numpy as np
import pyautogui
import mss
import time
import json
import os
import subprocess
import sys
from collections import deque

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

PARAMS_FILE = "learned_params.json"

class AimAI:
    def __init__(self):
        self.sct = mss.MSS()
        self.running = False
        self.shots_fired = 0
        self.last_positions = deque(maxlen=5)
        
        self.min_target_size = 8
        self.max_target_size = 300
        self.smoothing = 0.3
        self.click_delay = 0.08
        
        self.use_scrot = self._check_scrot()
        
        if not os.path.exists(PARAMS_FILE):
            print(f"ERROR: {PARAMS_FILE} not found. Run ./learn.sh first.")
            sys.exit(1)
        
        with open(PARAMS_FILE) as f:
            params = json.load(f)
        
        self.lower_hsv = np.array(params["lower_hsv"])
        self.upper_hsv = np.array(params["upper_hsv"])
        print(f"Loaded params from {params['sample_count']} clicks")
        print(f"HSV: {self.lower_hsv.astype(int)} -> {self.upper_hsv.astype(int)}")
        
    def _check_scrot(self):
        try:
            subprocess.run(["scrot", "--version"], capture_output=True, check=False)
            return True
        except FileNotFoundError:
            return False
    
    def get_screen(self):
        if self.use_scrot:
            try:
                path = "/tmp/aim_capture.png"
                subprocess.run(["scrot", "-o", path], capture_output=True, check=True, timeout=2)
                img = cv2.imread(path)
                if img is not None and img.mean() > 5:
                    return img, self.sct.monitors[1]
            except Exception:
                pass
        
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def detect_targets(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        targets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_target_size**2 < area < self.max_target_size**2:
                M = cv2.moments(cnt)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    targets.append((cx, cy, area))
        
        targets.sort(key=lambda t: t[2], reverse=True)
        return targets
    
    def aim_and_click(self, tx, ty, monitor):
        screen_x = monitor["left"] + tx
        screen_y = monitor["top"] + ty
        
        cx, cy = pyautogui.position()
        nx = int(cx * self.smoothing + screen_x * (1 - self.smoothing))
        ny = int(cy * self.smoothing + screen_y * (1 - self.smoothing))
        
        pyautogui.moveTo(nx, ny, duration=0.005)
        pyautogui.click()
        self.shots_fired += 1
        
    def run(self):
        print("=" * 50)
        print("AI PLAYING")
        print("=" * 50)
        if self.use_scrot:
            print("Capture: scrot")
        else:
            print("Capture: mss (install scrot for better results)")
        print("Stop: mouse to top-left corner or Ctrl+C")
        print("Starting in 3s...")
        time.sleep(3)
        
        self.running = True
        last_click = 0
        
        try:
            while self.running:
                img, monitor = self.get_screen()
                targets = self.detect_targets(img)
                
                if targets:
                    tx, ty, area = targets[0]
                    print(f"Target ({tx}, {ty}) size={int(area)}   ", end="\r")
                    
                    if time.time() - last_click > self.click_delay:
                        if not self.last_positions or \
                           abs(tx - self.last_positions[-1][0]) > 15 or \
                           abs(ty - self.last_positions[-1][1]) > 15:
                            
                            self.aim_and_click(tx, ty, monitor)
                            self.last_positions.append((tx, ty))
                            last_click = time.time()
                            print(f"\n>>> SHOT ({tx}, {ty}) | {self.shots_fired}")
                else:
                    print("Searching...                              ", end="\r")
                
                time.sleep(0.015)
                
        except KeyboardInterrupt:
            print("\nStopped.")
        except pyautogui.FailSafeException:
            print("\nFailsafe.")
        finally:
            print(f"\nShots: {self.shots_fired}")

def main():
    AimAI().run()

if __name__ == "__main__":
    main()
