from __future__ import annotations
import csv
import time
import cv2
import mediapipe as mp
from utils_landmarks import extract_features

LABELS = list("ABCDEFG")  # change to your target set (e.g., A-Z, 0-9, YES, NO)
SAMPLES_PER_LABEL = 200

mp_hands = mp.solutions.hands

def collect():
    with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.5) as hands:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        with open('data/samples.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            # header: label + 63 features
            writer.writerow(['label'] + [f'f{i}' for i in range(63)])
            for lbl in LABELS:
                print(f"Prepare to record label '{lbl}' in 3 seconds. Show the sign clearly.")
                time.sleep(3)
                count = 0
                while count < SAMPLES_PER_LABEL:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    res = hands.process(rgb)
                    if res.multi_hand_landmarks:
                        feat = extract_features(res.multi_hand_landmarks[0].landmark)
                        if feat is not None:
                            writer.writerow([lbl] + feat.tolist())
                            count += 1
                    # UI
                    cv2.putText(frame, f"Label: {lbl}  {count}/{SAMPLES_PER_LABEL}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                    cv2.imshow('Collect', frame)
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC to abort
                        cap.release()
                        cv2.destroyAllWindows()
                        return
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    collect()