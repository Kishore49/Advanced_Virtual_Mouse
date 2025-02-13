# Virtual Mouse using Hand Gestures

## Overview
This project implements a **Virtual Mouse** using **OpenCV**, **MediaPipe**, and **PyAutoGUI**. The system detects hand gestures via webcam and translates them into mouse actions like moving the cursor, clicking, scrolling, and dragging.

## Features
- **Cursor Control**: Move the index finger to control the mouse cursor.
- **Click Actions**: Perform single, double, and right clicks using hand gestures.
- **Dragging**: Grab and move objects with a pinching motion.
- **Scrolling**: Use the middle finger gesture to scroll up/down and horizontally.

## Hand Gestures
| Gesture         | Action           |
|---------------|----------------|
| ✋ Open Hand  | Move cursor   |
| 👉 Index & Thumb Close  | Left Click   |
| ✌️ Two Fingers Close Quickly | Double Click  |
| 🤙 Thumb & Pinky Touching  | Right Click  |
| 🤏 Thumb & Index Pinch  | Drag  |
| ☝️ Middle Finger Up  | Scroll |

## Installation
### Prerequisites
Ensure you have Python installed. Then install the required libraries:
```sh
pip install opencv-python mediapipe pyautogui numpy
```

### Running the Virtual Mouse
```sh
python virtual_mouse.py
```

## Usage
- Keep your hand visible in the camera frame.
- Perform gestures as described above to control mouse actions.
- Press `q` to exit the application.

## Configuration
You can modify sensitivity settings in `virtual_mouse.py`:
```python
self.cursor_sens = 2.0  # Cursor speed
self.scroll_sens = 100  # Scrolling speed
self.click_threshold = 0.03  # Click sensitivity
self.drag_threshold = 0.05  # Drag sensitivity
```

## License
This project is open-source and available under the MIT License.

