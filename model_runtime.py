import joblib
import numpy as np

MODEL_PATH = "data/models/sign_classifier.pkl"

class GestureRecognizer:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

    def predict(self, landmarks):
        if landmarks is None:
            return None
        landmarks = np.array(landmarks).reshape(1, -1)
        return self.model.predict(landmarks)[0]
