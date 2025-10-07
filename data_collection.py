import cv2
import mediapipe as mp
import numpy as np
import os

# Setup Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Gesture settings
gesture_name = "Space"
output_dir = f"data/{gesture_name}"
os.makedirs(output_dir, exist_ok=True)

# Open webcam
cap = cv2.VideoCapture(1)

# Set camera resolution (try native/high)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

sample_count = 0

print(f"📸 Recording gesture '{gesture_name}' — Press ENTER to save, ESC to exit")

# Responsive window instead of forced fullscreen
window_name = "Gesture Capture"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)   # Allow resizing
cv2.resizeWindow(window_name, 1280, 720)          # Initial size

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Flip for mirror effect
    frame = cv2.flip(frame, 1)

    # Mediapipe processing
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Draw landmarks if hand detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow(window_name, frame)
    key = cv2.waitKey(1)

    if key == 27:  # ESC to quit
        break
    elif key == 13:  # ENTER to save
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
            hand_landmarks = results.multi_hand_landmarks[0]
            data = []
            for lm in hand_landmarks.landmark:
                data.extend([lm.x, lm.y, lm.z])

            # Save .npy file
            filename = os.path.join(output_dir, f"{gesture_name}_{sample_count}.npy")
            np.save(filename, np.array(data))
            print(f"💾 Saved sample #{sample_count} for '{gesture_name}'")
            sample_count += 1
        else:
            print("⚠ No hand detected — sample not saved.")

cap.release()
cv2.destroyAllWindows()
