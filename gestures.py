# youtube_gesture_controller.py

import cv2  # OpenCV for webcam input
import mediapipe as mp  # MediaPipe for hand landmark detection
import pyautogui  # To simulate YouTube key commands
import time  # Cooldown management

# ===========================
# Stage 1: Setup & Initialize
# ===========================
k
cap = cv2.VideoCapture(0)  # Start webcam
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

gesture_cooldowns = {}  # To manage time between repeated gestures
COOLDOWN_PERIOD = 1.5   # Cooldown time in seconds

# ===========================
# Stage 2: Finger Status Logic
# ===========================

def fingers_up(lmList):
    fingers = []

    # Thumb (x axis for left/right flip check)
    if lmList[4][1] > lmList[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Fingers (index to pinky)
    tipIds = [8, 12, 16, 20]
    for i in tipIds:
        if lmList[i][2] < lmList[i - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers  # Example: [1, 1, 0, 0, 0] → thumb & index up

# ===========================
# Stage 3: Gesture Recognition
# ===========================

def get_gesture_name(fingerStatus):
    if fingerStatus == [1, 1, 1, 1, 1]:
        return "Play"
    elif fingerStatus == [0, 0, 0, 0, 0]:
        return "Pause"
    elif fingerStatus == [0, 1, 1, 0, 0]:
        return "Volume Up"
    elif fingerStatus == [0, 0, 0, 1, 1]:
        return "Volume Down"
    elif fingerStatus == [0, 0, 0, 0, 1]:
        return "Next Video"
    elif fingerStatus == [1, 1, 1, 1, 0]:
        return "Previous Video"
    else:
        return "Unknown"

# ===========================
# Stage 4 & 5: Gesture Action with Cooldown
# ===========================

def perform_action(gesture):
    current_time = time.time()

    if gesture in gesture_cooldowns:
        elapsed = current_time - gesture_cooldowns[gesture]
        if elapsed < COOLDOWN_PERIOD:
            remaining = round(COOLDOWN_PERIOD - elapsed, 1)
            return f"{gesture} (Cooldown: {remaining}s)"

    # Perform actual key action
    if gesture == "Play" or gesture == "Pause":
        pyautogui.press('k')
    elif gesture == "Volume Up":
        pyautogui.press('up')
    elif gesture == "Volume Down":
        pyautogui.press('down')
    elif gesture == "Next Video":
        pyautogui.hotkey('shift', 'n')
    elif gesture == "Previous Video":
        pyautogui.press('j')

    gesture_cooldowns[gesture] = current_time
    return f"{gesture} (Executed)"

# ===========================
# Stage 6: Main Loop
# ===========================

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    # Gesture logic
    message = "No Hand"
    if lmList:
        fingerStatus = fingers_up(lmList)
        gesture = get_gesture_name(fingerStatus)
        if gesture != "Unknown":
            message = perform_action(gesture)
        else:
            message = "Gesture: Unknown"

    # Display gesture status
    cv2.putText(img, message, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

    cv2.imshow("YouTube Gesture Controller", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ===========================
# Cleanup
# ===========================
cap.release()
cv2.destroyAllWindows()

print("Switch to kYouTube and focus the tab. Test will run in 5 seconds...")
time.sleep(5)
pyautogui.press('k') 