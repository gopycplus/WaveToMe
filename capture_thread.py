from __future__ import annotations
import cv2
from PySide6.QtCore import QThread, Signal
import mediapipe as mp
from utils_landmarks import extract_features

mp_hands = mp.solutions.hands

class CaptureThread(QThread):
    frame_ready = Signal(object)          # BGR frame (numpy array)
    features_ready = Signal(object)       # feature vector or None

    def __init__(self, cam_index: int = 0, min_detection_confidence: float = 0.6, min_tracking_confidence: float = 0.5):
        super().__init__()
        self.cam_index = cam_index
        self._running = False
        self.det_conf = min_detection_confidence
        self.trk_conf = min_tracking_confidence

    def run(self):
        self._running = True
        cap = cv2.VideoCapture(self.cam_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=self.det_conf,
            min_tracking_confidence=self.trk_conf,
        ) as hands:
            while self._running:
                ok, frame = cap.read()
                if not ok:
                    break
                # Flip for selfie view
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = hands.process(rgb)

                feat = None
                if res.multi_hand_landmarks:
                    # take first hand
                    hand_lms = res.multi_hand_landmarks[0].landmark
                    feat = extract_features(hand_lms)
                    # Draw landmarks for user feedback
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame,
                        res.multi_hand_landmarks[0],
                        mp_hands.HAND_CONNECTIONS,
                    )

                self.features_ready.emit(feat)
                self.frame_ready.emit(frame)

        cap.release()

    def stop(self):
        self._running = False
        self.wait(500)