import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands

def extract_landmarks(results):
    if not results.multi_hand_landmarks:
        return None
    landmarks = []
    for hand_landmarks in results.multi_hand_landmarks:
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
    return np.array(landmarks)
