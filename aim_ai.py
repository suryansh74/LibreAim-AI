#!/usr/bin/env python3
"""
Aim Trainer AI - Uses parameters learned from your gameplay.
"""

import cv2
import numpy as np
import pyautogui
import mss
import time
import json
import sys
import os
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
        
        self.min_target_size = 6
        self.max_target_size = 250
        self.smoothing = 0.35
        self.click_delay = 0.07
        
        # Load learned parameters
        if not os.path.exists(PARAMS_FILE):
            print(f"ERROR: {PARAMS_FILE} not found.")
            print("Run the learning mode first: python learn.py")
            sys.exit(1)
        
        with open(PARAMS_FILE) as f:
            params = json.load(f)
        
        self.lower_hsv = np.array(params["lower_hsv"])
        self.upper_hsv = np.array(params["upper_hsv"])
        print(f"Loaded learned params from {params['sample_count']} clicks")
        print(f"HSV range: {self.lower_hsv} -> {self.upper_hsv}")
        
    def get_screen(self):
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def detect_targets(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        kernel = np.ones((4, 4), np.uint8)
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
    
    def aim_and_click(self, target_x, target_y, monitor):
        screen_x = monitor["left"] + target_x
        screen_y = monitor["top"] + target_y
        
        current_x, current_y = pyautogui.position()
        new_x = int(current_x * self.smoothing + screen_x * (1 - self.smoothing))
        new_y = int(current_y * self.smoothing + screen_y * (1 - self.smoothing))
        
        pyautogui.moveTo(new_x, new_y, duration=0.006)
        pyautogui.click()
        self.shots_fired += 1
        
    def run(self):
        print("=" * 50)
        print("AI PLAYING (using learned parameters)")
        print("=" * 50)
        print("Move mouse to TOP-LEFT corner to stop")
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        self.running = True
        last_click = 0
        
        try:
            while self.running:
                img, monitor = self.get_screen()
                targets = self.detect_targets(img)
                
                if targets:
                    tx, ty, area = targets[0]
                    print(f"Target at ({tx}, {ty}) size={int(area)}   ", end="\r")
                    
                    if time.time() - last_click > self.click_delay:
                        if len(self.last_positions) == 0 or \
                           abs(tx - self.last_positions[-1][0]) > 10 or \
                           abs(ty - self.last_positions[-1][1]) > 10:
                            
                            self.aim_and_click(tx, ty, monitor)
                            self.last_positions.append((tx, ty))
                            last_click = time.time()
                            print(f"\n>>> SHOT ({tx}, {ty}) | Total: {self.shots_fired}")
                else:
                    print("Searching...                                              ", end="\r")
                
                time.sleep(0.008)
                
        except KeyboardInterrupt:
            print("\nStopped by user.")
        except pyautogui.FailSafeException:
            print("\nStopped (mouse to corner).")
        finally:
            print(f"\nTotal shots: {self.shots_fired}")

def main():
    import sys
    AimAI().run()

if __name__ == "__main__":
    main()
