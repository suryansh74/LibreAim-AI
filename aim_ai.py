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
        self.min_target_size = 8
        self.max_target_size = 200
        self.aim_offset_x = 0
        self.aim_offset_y = 0
        self.smoothing = 0.4
        self.click_delay = 0.08
        
        # Broader yellow/gold range for LibreAim
        self.lower_yellow = np.array([10, 50, 100])
        self.upper_yellow = np.array([45, 255, 255])
        
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
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        targets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if self.min_target_size**2 < area < self.max_target_size**2:
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.4:
                        M = cv2.moments(cnt)
                        if M["m00"] > 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            targets.append((cx, cy, area))
        
        targets.sort(key=lambda t: t[2], reverse=True)
        return targets
    
    def aim_and_click(self, target_x, target_y, monitor):
        """Move mouse to target and click"""
        screen_x = monitor["left"] + target_x + self.aim_offset_x
        screen_y = monitor["top"] + target_y + self.aim_offset_y
        
        current_x, current_y = pyautogui.position()
        new_x = int(current_x * self.smoothing + screen_x * (1 - self.smoothing))
        new_y = int(current_y * self.smoothing + screen_y * (1 - self.smoothing))
        
        pyautogui.moveTo(new_x, new_y, duration=0.01)
        time.sleep(0.01)
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
        print("1. Start LibreAim")
        print("2. Select a scenario (e.g. Random targets)")
        print("3. Click Play so targets appear")
        print("4. Keep the game window visible and unpaused")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        self.running = True
        last_click_time = 0
        frame_count = 0
        
        try:
            while self.running:
                img, monitor = self.get_screen()
                targets = self.detect_targets(img)
                frame_count += 1
                
                if targets:
                    tx, ty, area = targets[0]
                    print(f"Detected {len(targets)} target(s) | Largest at ({tx}, {ty}) size={int(area)}", end="\r")
                    
                    if (time.time() - last_click_time) > self.click_delay:
                        if len(self.last_positions) == 0 or \
                           abs(tx - self.last_positions[-1][0]) > 10 or \
                           abs(ty - self.last_positions[-1][1]) > 10:
                            
                            self.aim_and_click(tx, ty, monitor)
                            self.last_positions.append((tx, ty))
                            last_click_time = time.time()
                            print(f"\n>>> SHOT at ({tx}, {ty}) | Total shots: {self.shots_fired}")
                else:
                    if frame_count % 30 == 0:
                        print("No targets detected... (is the game running and unpaused?)", end="\r")
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nStopped by user.")
        except pyautogui.FailSafeException:
            print("\n\nStopped by failsafe (mouse moved to corner).")
        finally:
            self.running = False
            print(f"\nTotal shots fired: {self.shots_fired}")
            print("AI stopped.")

def main():
    print("LibreAim AI - Yellow Target Detector")
    print("-" * 40)
    print("This version is tuned for LibreAim's yellow spheres.")
    print()
    input("Press Enter to start...")
    
    ai = AimAI()
    ai.run()

if __name__ == "__main__":
    main()
