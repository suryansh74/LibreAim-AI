#!/usr/bin/env python3
"""
Aim Trainer AI - LibreAim Yellow Targets
With color calibration debug.
"""

import cv2
import numpy as np
import pyautogui
import mss
import time
from collections import deque

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.001

class AimAI:
    def __init__(self):
        self.sct = mss.MSS()
        self.running = False
        self.shots_fired = 0
        self.last_positions = deque(maxlen=5)
        
        self.min_target_size = 5
        self.max_target_size = 300
        self.smoothing = 0.3
        self.click_delay = 0.06
        
        # Very wide yellow-gold range
        self.lower_yellow = np.array([5, 30, 60])
        self.upper_yellow = np.array([55, 255, 255])
        
    def get_screen(self):
        monitor = self.sct.monitors[1]
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, monitor
    
    def sample_colors(self, img):
        """Print some color samples from the image for debugging"""
        h, w = img.shape[:2]
        # Sample center area where targets usually are
        cy, cx = h // 2, w // 2
        samples = [
            img[cy, cx],
            img[cy-50, cx],
            img[cy+50, cx],
            img[cy, cx-100],
            img[cy, cx+100],
        ]
        print("\n--- Color samples (BGR) ---")
        for i, s in enumerate(samples):
            hsv = cv2.cvtColor(np.uint8([[s]]), cv2.COLOR_BGR2HSV)[0][0]
            print(f"  Sample {i}: BGR={s}  HSV={hsv}")
        print("---------------------------\n")
    
    def detect_targets(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        
        kernel = np.ones((4, 4), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Save debug
        cv2.imwrite("/tmp/aim_debug_mask.png", mask)
        cv2.imwrite("/tmp/aim_debug_screen.png", img)
        
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
        
        pyautogui.moveTo(new_x, new_y, duration=0.005)
        pyautogui.click()
        self.shots_fired += 1
        
    def run(self):
        print("=" * 50)
        print("LIBREAIM AI - COLOR DEBUG MODE")
        print("=" * 50)
        print("Starting in 3 seconds...")
        print("Keep LibreAim visible with targets on screen!")
        time.sleep(3)
        
        self.running = True
        last_click = 0
        start_time = time.time()
        sampled = False
        
        try:
            while self.running:
                img, monitor = self.get_screen()
                
                # Sample colors once after 1 second
                if not sampled and (time.time() - start_time) > 1:
                    self.sample_colors(img)
                    sampled = True
                
                targets = self.detect_targets(img)
                
                if targets:
                    tx, ty, area = targets[0]
                    print(f"FOUND {len(targets)} target(s) at ({tx}, {ty}) size={int(area)}   ", end="\r")
                    
                    if time.time() - last_click > self.click_delay:
                        self.aim_and_click(tx, ty, monitor)
                        last_click = time.time()
                        print(f"\n>>> CLICKED ({tx}, {ty}) | Shots: {self.shots_fired}")
                else:
                    print("No targets found...                                              ", end="\r")
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopped.")
        except pyautogui.FailSafeException:
            print("\nFailsafe triggered.")
        finally:
            print(f"\nShots: {self.shots_fired}")
            print("Debug images: /tmp/aim_debug_mask.png , /tmp/aim_debug_screen.png")

def main():
    input("Press Enter when targets are visible on screen...")
    AimAI().run()

if __name__ == "__main__":
    main()
