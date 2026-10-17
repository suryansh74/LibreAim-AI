#!/usr/bin/env python3
"""
Aim Trainer AI - Tuned for LibreAim (Yellow Targets)
Detects yellow spheres and automatically aims + clicks.
"""

import cv2
import numpy as np
import pyautogui
import mss
import time
import sys
from collections import deque

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

class AimAI:
    def __init__(self):
        self.sct = mss.MSS()
        self.running = False
        self.shots_fired = 0
        self.last_positions = deque(maxlen=5)
        
        # Detection settings
        self.min_target_size = 12
        self.max_target_size = 120
        self.aim_offset_x = 0
        self.aim_offset_y = 0
        self.smoothing = 0.5
        self.click_delay = 0.06
        
        # Yellow target detection (LibreAim spheres)
        # HSV range for yellow/gold
        self.lower_yellow = np.array([15, 80, 150])
        self.upper_yellow = np.array([40, 255, 255])
        
    def get_screen(self):
        """Capture the primary monitor"""
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def detect_targets(self, img):
        """Detect yellow spherical targets"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Yellow mask
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        
        # Clean up
        kernel = np.ones((4, 4), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        targets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_target_size**2 < area < self.max_target_size**2:
                # Circularity check (spheres should be roughly circular)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.5:  # Reasonably circular
                        M = cv2.moments(cnt)
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            targets.append((cx, cy, area))
        
        # Prefer larger targets
        targets.sort(key=lambda t: t[2], reverse=True)
        return targets
    
    def aim_and_click(self, target_x, target_y, monitor):
        """Move mouse to target and click"""
        screen_x = monitor["left"] + target_x + self.aim_offset_x
        screen_y = monitor["top"] + target_y + self.aim_offset_y
        
        current_x, current_y = pyautogui.position()
        new_x = int(current_x * self.smoothing + screen_x * (1 - self.smoothing))
        new_y = int(current_y * self.smoothing + screen_y * (1 - self.smoothing))
        
        pyautogui.moveTo(new_x, new_y, duration=0.008)
        time.sleep(0.008)
        pyautogui.click()
        self.shots_fired += 1
        
    def run(self):
        """Main loop"""
        print("=" * 50)
        print("LIBREAIM AI STARTED (Yellow Target Mode)")
        print("=" * 50)
        print("Controls:")
        print("  - Move mouse to TOP-LEFT corner to STOP")
        print("  - Press Ctrl+C in terminal to stop")
        print()
        print("Make sure LibreAim is visible (windowed mode recommended)")
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        self.running = True
        last_click_time = 0
        
        try:
            while self.running:
                img, monitor = self.get_screen()
                targets = self.detect_targets(img)
                
                if targets:
                    print(f"Detected {len(targets)} target(s) | Largest at ({targets[0][0]}, {targets[0][1]})", end="\r")
                    if (time.time() - last_click_time) > self.click_delay:
                    tx, ty, area = targets[0]
                    
                    # Avoid re-clicking same spot
                    if len(self.last_positions) == 0 or \
                       abs(tx - self.last_positions[-1][0]) > 8 or \
                       abs(ty - self.last_positions[-1][1]) > 8:
                        
                        self.aim_and_click(tx, ty, monitor)
                        self.last_positions.append((tx, ty))
                        last_click_time = time.time()
                        
                        print(f"\nShot at ({tx}, {ty}) | Targets: {len(targets)} | Total shots: {self.shots_fired}")
                
                else:
                    print("No targets detected... (make sure game is unpaused and window is visible)", end="\r")
                
        except KeyboardInterrupt:
            print("\nStopped by user.")
        except pyautogui.FailSafeException:
            print("\nStopped by failsafe (mouse moved to corner).")
        finally:
            self.running = False
            print(f"\nTotal shots: {self.shots_fired}")
            print("AI stopped.")

def main():
    print("LibreAim AI - Yellow Target Detector")
    print("-" * 40)
    print("This version is tuned for LibreAim's yellow spheres.")
    print()
    print("Press Enter to start...")
    input()
    
    ai = AimAI()
    ai.run()

if __name__ == "__main__":
    main()
