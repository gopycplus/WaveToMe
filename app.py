from __future__ import annotations
import sys
import cv2
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTextEdit, QFileDialog, QMessageBox
)

from main import SignRecognizer
from smoothing import MajoritySmoother


def cv2qt(img_bgr: np.ndarray) -> QPixmap:
    h, w, ch = img_bgr.shape
    bytes_per_line = ch * w
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖐 Sign2Text Professional")
        self.setFixedSize(1200, 750)
        self.setStyleSheet(self.get_stylesheet())

        self.init_ui()
        self.init_camera()
        self.init_sign_recognizer()

    def get_stylesheet(self) -> str:
        return """
            QWidget { background-color: #121212; color: #EEE; }
            QPushButton {
                background-color: #1E1E1E;
                border: 1px solid #333;
                padding: 8px 14px;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #292929; }
            QPushButton:pressed { background-color: #333; }
            QLabel { font-size: 15px; }
            QTextEdit {
                background: #1A1A1A; border-radius: 10px;
                border: 1px solid #333; color: #EEE;
                padding: 8px; font-size: 15px;
            }
        """

    def init_ui(self):
        # Video label
        self.video_label = QLabel("Camera is off")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(800, 600)
        self.video_label.setStyleSheet(
            "background:#000; border-radius:15px; border:2px solid #333;"
        )

        # Prediction label
        self.pred_label = QLabel("—")
        self.pred_label.setAlignment(Qt.AlignCenter)
        self.pred_label.setStyleSheet(
            "font-size:32px; font-weight:bold; color:#4CAF50; padding:10px;"
        )

        # Output text area
        self.output = QTextEdit()
        self.output.setPlaceholderText("Predicted text will appear here…")
        self.output.setFixedHeight(160)

        # Control buttons
        self.create_buttons()

        # Layouts
        self.setup_layouts()

    def create_buttons(self):
        self.btn_start = QPushButton("▶ Start Camera")
        self.btn_stop = QPushButton("⏹ Stop Camera")
        self.btn_load = QPushButton("📂 Load Model")
        self.btn_space = QPushButton("␣ Space")
        self.btn_back = QPushButton("⌫ Backspace")
        self.btn_clear = QPushButton("🧹 Clear")
        self.btn_commit = QPushButton("✔ Commit")

        # Button connections
        self.btn_start.clicked.connect(self.start_cam)
        self.btn_stop.clicked.connect(self.stop_cam)
        self.btn_load.clicked.connect(self.load_model)
        self.btn_space.clicked.connect(self.add_space)
        self.btn_back.clicked.connect(self.backspace)
        self.btn_clear.clicked.connect(self.clear_text)
        self.btn_commit.clicked.connect(self.commit_token)

    def setup_layouts(self):
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.btn_start)
        top_layout.addWidget(self.btn_stop)
        top_layout.addWidget(self.btn_load)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Current Token:"))
        right_layout.addWidget(self.pred_label)
        right_layout.addWidget(QLabel("Output:"))
        right_layout.addWidget(self.output)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.btn_space)
        btns_layout.addWidget(self.btn_back)
        btns_layout.addWidget(self.btn_clear)
        btns_layout.addWidget(self.btn_commit)
        right_layout.addLayout(btns_layout)

        mid_layout = QHBoxLayout()
        mid_layout.addWidget(self.video_label)
        mid_layout.addLayout(right_layout)

        root_layout = QVBoxLayout()
        root_layout.addLayout(top_layout)
        root_layout.addLayout(mid_layout)
        self.setLayout(root_layout)

    def init_camera(self):
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def init_sign_recognizer(self):
        self.recognizer = SignRecognizer("models/sign_classifier.pkl")
        self.smoother = MajoritySmoother(window=7)

    def start_cam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)

    def stop_cam(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.video_label.setText("Camera is off")

    def load_model(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select model", "models", "Pickle (*.pkl)")
        if fn:
            try:
                self.recognizer = SignRecognizer(fn)
            except Exception as e:
                QMessageBox.warning(self, "Load failed", str(e))

    def update_frame(self):
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        frame, pred, fps = self.recognizer.process_frame(frame)
        smoothed = self.smoother.push(pred)
        if smoothed:
            self.pred_label.setText(smoothed)
        self.video_label.setPixmap(cv2qt(frame))

    def commit_token(self):
        token = self.pred_label.text()
        if token and token != "—":
            self.output.insertPlainText(token)

    def add_space(self):
        self.output.insertPlainText(" ")

    def backspace(self):
        cur = self.output.toPlainText()
        if cur:
            self.output.setPlainText(cur[:-1])
            cursor = self.output.textCursor()
            cursor.movePosition(cursor.End)
            self.output.setTextCursor(cursor)

    def clear_text(self):
        self.output.clear()

    def closeEvent(self, e):
        self.stop_cam()
        super().closeEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())