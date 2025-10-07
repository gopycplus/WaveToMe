import os
import cv2
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import mediapipe as mp

# Paths
WEBCAM_DATA_DIR = "data"  # your own .npy gesture folders
EXTERNAL_IMG_DIR = "external_asl_images/combine_asl_dataset"  # images from Kaggle dataset
MODEL_PATH = "models/sign_classifier.pkl"

# Setup Mediapipe for landmark extraction
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def extract_landmarks_from_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    if not results.multi_hand_landmarks:
        return None
    # take the first hand
    landmarks = []
    for lm in results.multi_hand_landmarks[0].landmark:
        landmarks.extend([lm.x, lm.y, lm.z])
    return np.array(landmarks, dtype=np.float32)

X, y = [], []

# 1. From external image dataset
# for label in os.listdir(EXTERNAL_IMG_DIR):
#     label_dir = os.path.join(EXTERNAL_IMG_DIR, label)
#     if os.path.isdir(label_dir):
#         for fname in os.listdir(label_dir):
#             if fname.lower().endswith((".jpg", ".jpeg", ".png")):
#                 img_path = os.path.join(label_dir, fname)
#                 print(f"[EXTERNAL DATA] Processing {img_path}")
#                 pts = extract_landmarks_from_image(img_path)
#                 if pts is not None:
#                     X.append(pts)
#                     y.append(label)
#                 else:
#                     print(f"⚠️ No hand detected in {img_path}")

# 2. From your webcam-collected .npy files
for gesture in reversed(os.listdir(WEBCAM_DATA_DIR)):
    gesture_path = os.path.join(WEBCAM_DATA_DIR, gesture)
    if os.path.isdir(gesture_path):
        for fname in reversed(os.listdir(gesture_path)):
            if fname.endswith(".npy"):
                file_path = os.path.join(gesture_path, fname)
                print(f"[WEBCAM DATA] Loading {file_path}")
                X.append(np.load(file_path))
                y.append(gesture)

X = np.array(X)
y = np.array(y)

print(f"Training on {len(X)} samples across {len(set(y))} classes.")

clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X, y)

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(clf, MODEL_PATH)
print(f"Saved trained model to {MODEL_PATH}")
