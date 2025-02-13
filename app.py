import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from collections import deque
from enum import Enum
import time

class Gesture(Enum):
    OPEN = "Open Hand"
    CLICK = "Single Click"
    DBL_CLICK = "Double Click"
    DRAG = "Dragging"
    SCROLL = "Scrolling"
    RIGHT_CLICK = "Right Click"

class VirtualMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7)
        
        # Configuration
        self.smoothing_factor = 7
        self.cursor_sens = 1.4
        self.scroll_sens = 120
        self.click_threshold = 0.05
        self.dbl_click_threshold = 0.3
        self.drag_threshold = 0.08
        
        # State tracking
        self.history = deque(maxlen=self.smoothing_factor)
        self.last_click_time = 0
        self.dragging = False
        self.last_gesture = Gesture.OPEN
        self.screen_size = pyautogui.size()
        
        # Initialize drawing utils
        self.mp_drawing = mp.solutions.drawing_utils
        self.click_radius = 20

    def get_hand_landmarks(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        return results.multi_hand_landmarks

    def get_finger_state(self, landmarks):
        fingers = []
        tip_ids = [4, 8, 12, 16, 20]
        
        for tid in tip_ids:
            finger = landmarks[tid]
            if tid == 4:
                fingers.append(finger.x < landmarks[tid - 1].x - 0.05)
            else:
                fingers.append(finger.y < landmarks[tid - 2].y - 0.03)
        return fingers

    def process_gestures(self, landmarks, frame, x_smooth, y_smooth): 
        gesture = Gesture.OPEN
        fingers = self.get_finger_state(landmarks)
        h, w, _ = frame.shape
        
        # Calculate normalized distance between thumb and index
        thumb = landmarks[4]
        index = landmarks[8]
        distance = np.hypot(thumb.x - index.x, thumb.y - index.y)
        pinky = landmarks[20]

        # Click detection
        if distance < self.click_threshold:
            current_time = time.time()
            time_diff = current_time - self.last_click_time
            
            if time_diff < self.dbl_click_threshold:
                pyautogui.doubleClick()
                gesture = Gesture.DBL_CLICK
            else:
                pyautogui.click()
                gesture = Gesture.CLICK
            self.last_click_time = current_time
        
        # Right click detection
        elif np.hypot(thumb.x - pinky.x, thumb.y - pinky.y) < self.click_threshold:
            pyautogui.rightClick()
            gesture = Gesture.RIGHT_CLICK
        
        # Drag detection
        elif self.dragging and distance < self.drag_threshold:
            pyautogui.dragTo(x_smooth, y_smooth, duration=0.1) 
            gesture = Gesture.DRAG
        elif distance < self.drag_threshold:
            self.dragging = True
            pyautogui.mouseDown()
            gesture = Gesture.DRAG
        else:
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False
        
        # Scroll detection
        if fingers[2]:
            gesture = Gesture.SCROLL
            middle = landmarks[12]
            delta_x = middle.x - landmarks[9].x
            delta_y = middle.y - landmarks[9].y
            pyautogui.scroll(int(delta_y * self.scroll_sens))
            if abs(delta_x) > 0.1:
                pyautogui.hscroll(int(delta_x * self.scroll_sens))
        
        return gesture

    def smooth_cursor(self, x, y):
        self.history.append((x, y))
        avg_x = np.mean([pos[0] for pos in self.history])
        avg_y = np.mean([pos[1] for pos in self.history])
        return int(avg_x), int(avg_y)

    def draw_gesture_feedback(self, frame, gesture):
        color_map = {
            Gesture.OPEN: (100, 255, 100),
            Gesture.CLICK: (255, 0, 0),
            Gesture.DBL_CLICK: (0, 0, 255),
            Gesture.DRAG: (255, 255, 0),
            Gesture.SCROLL: (0, 255, 255),
            Gesture.RIGHT_CLICK: (255, 0, 255)
        }
        cv2.circle(frame, (80, 80), 50, color_map[gesture], -1)
        cv2.putText(frame, gesture.value, (150, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

    def run(self):
        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            landmarks = self.get_hand_landmarks(frame)
            
            if landmarks:
                hand = landmarks[0]
                self.mp_drawing.draw_landmarks(
                    frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
                
                index = hand.landmark[8]
                x = int(index.x * self.screen_size.width)
                y = int(index.y * self.screen_size.height)
                x_smooth, y_smooth = self.smooth_cursor(x, y)
                
                # Pass smoothed coordinates to gesture processor
                gesture = self.process_gestures(hand.landmark, frame, x_smooth, y_smooth)
                
                if gesture not in [Gesture.CLICK, Gesture.DBL_CLICK, Gesture.RIGHT_CLICK]:
                    pyautogui.moveTo(
                        x_smooth * self.cursor_sens,
                        y_smooth * self.cursor_sens,
                        duration=0.05
                    )
                
                self.draw_gesture_feedback(frame, gesture)

            cv2.imshow('Advanced Virtual Mouse', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    vm = VirtualMouse()
    vm.run()
