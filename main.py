import cv2
import mediapipe as mp
import numpy as np
import joblib
import customtkinter as ctk
from PIL import Image
import time
import threading
from gtts import gTTS
import pygame
import tempfile
import os
import json

SETTINGS_FILE = "settings.json"

LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr", "German": "de",
    "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Chinese": "zh", "Arabic": "ar", "Hindi": "hi", "Uzbek": "uz"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"language": "English", "language_code": "en", "gender": "Male", "speed": 3.0}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def center_window(win, width, height):
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# ------------------------------------------------------------------------------------------------
# Settings Window
# ----------------------------------------------------------------------
def open_settings_window(root):
    settings = load_settings()

    win = ctk.CTkToplevel(root)
    win.title("Settings - WaveToMe")
    win.geometry("480x380")
    win.configure(fg_color="#1c1e24")
    win.resizable(False, False)
    center_window(win, 480, 380)

    frame = ctk.CTkFrame(win, fg_color="#2b2f38", corner_radius=15)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    title = ctk.CTkLabel(frame, text="Settings", font=("Segoe UI", 32, "bold"))
    title.pack(pady=(15, 0))

    # Language
    lang_label = ctk.CTkLabel(frame, text="Reader Language:", font=("Segoe UI", 14))
    lang_label.pack(pady=(0, 5))
    lang_var = ctk.StringVar(value=settings.get("language", "English"))
    lang_dropdown = ctk.CTkOptionMenu(frame,
                                      values=list(LANGUAGES.keys()),
                                      variable=lang_var, width=200,
                                      fg_color="#3a3f4b", button_color="#4a90e2")
    lang_dropdown.pack()

    # Gender
    gender_label = ctk.CTkLabel(frame, text="Reader Gender:", font=("Segoe UI", 14))
    gender_label.pack(pady=(5, 5))
    gender_var = ctk.StringVar(value=settings.get("gender", "Male"))
    gender_dropdown = ctk.CTkOptionMenu(frame,
                                        values=["Male", "Female", "Neutral"],
                                        variable=gender_var, width=200,
                                        fg_color="#3a3f4b", button_color="#4a90e2")
    gender_dropdown.pack()

    # Speed
    speed_label = ctk.CTkLabel(frame, text="Sign Recognition Speed (chars/sec):", font=("Segoe UI", 14))
    speed_label.pack(pady=(5))
    speed_var = ctk.DoubleVar(value=settings.get("speed", 3.0))
    speed_slider = ctk.CTkSlider(frame,
                                 from_=1.0, to=10.0, number_of_steps=9,
                                 variable=speed_var,
                                 progress_color="#4a90e2", button_color="#4a90e2", width=220)
    speed_slider.pack()
    speed_value = ctk.CTkLabel(frame, text=f"{speed_var.get():.1f}", font=("Segoe UI", 12))
    speed_value.pack()

    def update_speed(val):
        speed_value.configure(text=f"{float(val):.1f}")

    speed_slider.configure(command=update_speed)

    # Save and Close buttons
    def save_and_close():
        chosen_settings = {
            "language": lang_var.get(),
            "language_code": LANGUAGES[lang_var.get()],
            "gender": gender_var.get(),
            "speed": speed_var.get()
        }
        save_settings(chosen_settings)
        print("Settings saved:", chosen_settings)
        win.destroy()

    def close_without_save():
        win.destroy()

    button_frame = ctk.CTkFrame(frame, fg_color="transparent")
    button_frame.pack(pady=10)

    save_btn = ctk.CTkButton(button_frame, text="Save", command=save_and_close,
                             fg_color="#4a90e2", hover_color="#357abd", width=120, height=40)
    save_btn.pack(side="left", padx=(0, 10))

    close_btn = ctk.CTkButton(button_frame, text="Close", command=close_without_save,
                              fg_color="#6c757d", hover_color="#5a6268", width=120, height=40)
    close_btn.pack(side="left")

    win.grab_set()


# -------------------------------------------------------------------------
# Load trained model
# ------------------------------------------------------------------------------------
model = joblib.load("models/sign_classifier_v3.pkl")

# --------------------------------------------------------------------------------------
# Mediapipe setup
# ------------------------------------------------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --------------------------------------------------------------------------------
# Webcam
# ------------------------------------------------------------------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ----------------------------------------------------------------------------------------
# GUI Setup
# ---------------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("WaveToMe - Sign Language Translator")
root.geometry("1200x800")
root.configure(fg_color="#0f1419")

# ---------------------------------------------------------------------------------------------------
# Left Panel
# -------------------------------------------------------------------------------
left_panel = ctk.CTkFrame(root, fg_color="#1a1f2e", corner_radius=15)
left_panel.place(relx=0.015, rely=0.025, relwidth=0.575, relheight=0.95)

left_panel.grid_rowconfigure(0, weight=0)
left_panel.grid_rowconfigure(1, weight=1)
left_panel.grid_rowconfigure(2, weight=0)
left_panel.grid_columnconfigure(0, weight=1)

# Header
header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

title_label = ctk.CTkLabel(
    header_frame,
    text="📹 Live Camera",
    font=("Segoe UI", 24, "bold"),
    text_color="#ffffff"
)
title_label.pack(side="left")

# Status indicator
status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
status_frame.pack(side="right")

status_dot = ctk.CTkLabel(
    status_frame,
    text="●",
    font=("Segoe UI", 20),
    text_color="#10a37f"
)
status_dot.pack(side="left", padx=(0, 5))

status_label = ctk.CTkLabel(
    status_frame,
    text="Ready",
    font=("Segoe UI", 14),
    text_color="#a0a0a0"
)
status_label.pack(side="left")

# Camera container
camera_container = ctk.CTkFrame(left_panel, fg_color="#0f1419", corner_radius=12, border_width=2,
                                border_color="#2a2f3e")
camera_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
camera_container.grid_rowconfigure(0, weight=1)
camera_container.grid_columnconfigure(0, weight=1)

video_label = ctk.CTkLabel(camera_container, text="", fg_color="transparent")
video_label.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

# Confidence indicator
confidence_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
confidence_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

confidence_label = ctk.CTkLabel(
    confidence_frame,
    text="Detection Confidence:",
    font=("Segoe UI", 13),
    text_color="#a0a0a0"
)
confidence_label.pack(side="left")

confidence_value = ctk.CTkLabel(
    confidence_frame,
    text="--",
    font=("Segoe UI", 13, "bold"),
    text_color="#10a37f"
)
confidence_value.pack(side="left", padx=10)

confidence_bar = ctk.CTkProgressBar(
    confidence_frame,
    width=200,
    height=8,
    progress_color="#10a37f",
    fg_color="#2a2f3e"
)
confidence_bar.pack(side="left", padx=10)
confidence_bar.set(0)

# --------------------------------------------------------------------------------------------------------
# Right Panel
# ------------------------------------------------------------------------------------
right_panel = ctk.CTkFrame(root, fg_color="#1a1f2e", corner_radius=15)
right_panel.place(relx=0.605, rely=0.025, relwidth=0.38, relheight=0.95)

right_panel.grid_rowconfigure(0, weight=0)
right_panel.grid_rowconfigure(1, weight=1)
right_panel.grid_rowconfigure(2, weight=0)
right_panel.grid_columnconfigure(0, weight=1)

# Output header
output_header = ctk.CTkLabel(
    right_panel,
    text="📝 Translated Text",
    font=("Segoe UI", 22, "bold"),
    text_color="#ffffff"
)
output_header.grid(row=0, column=0, sticky="w", padx=15, pady=(20, 10))

# Add settings button (⚙️) next to output header
settings_btn = ctk.CTkButton(
    right_panel,
    text="⚙️",
    width=45,
    height=45,
    corner_radius=10,
    fg_color="#2a2f3e",
    hover_color="#3a3f4e",
    text_color="#ffffff",
    font=("Segoe UI", 18, "bold"),
    command=lambda: open_settings_window(root)
)
settings_btn.grid(row=0, column=0, sticky="e", padx=15, pady=(20, 10))

# Text output box
text_box = ctk.CTkTextbox(
    right_panel,
    font=("Segoe UI", 18),
    fg_color="#0f1419",
    text_color="#ffffff",
    border_width=2,
    border_color="#2a2f3e",
    wrap="word",
    corner_radius=12
)
text_box.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

# Action buttons
action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
action_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 20))
action_frame.grid_columnconfigure(0, weight=1)
action_frame.grid_columnconfigure(1, weight=1)

# --------------------------------------------------------------------------------------
# Google TTS Engine Setup
# -------------------------------------------------------------------------------------
pygame.mixer.init()

is_speaking = False
temp_audio_file = None


def stop_speech():
    global is_speaking, temp_audio_file
    if is_speaking:
        try:
            pygame.mixer.music.stop()
            if temp_audio_file and os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
        except:
            pass
    is_speaking = False
    status_label.configure(text="Ready")
    status_dot.configure(text_color="#10a37f")


def speak_text():
    global is_speaking, temp_audio_file
    settings = load_settings()

    content = text_box.get("1.0", "end-1c").strip()
    if not content:
        status_label.configure(text="No text to speak")
        root.after(1500, lambda: status_label.configure(text="Ready"))
        return

    if is_speaking:
        status_label.configure(text="Already speaking...")
        return

    def speak_in_thread():
        global is_speaking, temp_audio_file
        is_speaking = True
        try:
            status_label.configure(text="Generating speech...")
            status_dot.configure(text_color="#fbbf24")

            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name

            lang_code = settings["language_code"]
            tts_obj = gTTS(text=content, lang=lang_code, slow=False)
            tts_obj.save(temp_audio_file)

            status_label.configure(text="Speaking...")
            status_dot.configure(text_color="#3b82f6")

            pygame.mixer.music.load(temp_audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
        except Exception as e:
            print(f"TTS Error: {e}")
            status_label.configure(text="Speech error")
            root.after(2000, lambda: status_label.configure(text="Ready"))
        finally:
            is_speaking = False
            temp_audio_file = None
            status_label.configure(text="Ready")
            status_dot.configure(text_color="#10a37f")

    threading.Thread(target=speak_in_thread, daemon=True).start()


clear_btn = ctk.CTkButton(
    action_frame,
    text="🗑️ Clear",
    height=45,
    corner_radius=10,
    fg_color="#2a2f3e",
    hover_color="#3a3f4e",
    text_color="#ffffff",
    font=("Segoe UI", 16, "bold"),
    command=lambda: (stop_speech(), text_box.delete("1.0", "end"))
)
clear_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

speak_btn = ctk.CTkButton(
    action_frame,
    text="🔊 Speak",
    height=45,
    corner_radius=10,
    fg_color="#10a37f",
    hover_color="#0d8a6b",
    text_color="#ffffff",
    font=("Segoe UI", 16, "bold"),
    command=speak_text
)
speak_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))

copy_btn = ctk.CTkButton(
    action_frame,
    text="📋 Copy",
    height=45,
    corner_radius=10,
    fg_color="#3b82f6",
    hover_color="#2563eb",
    text_color="#ffffff",
    font=("Segoe UI", 16, "bold"),
    command=lambda: root.clipboard_clear() or root.clipboard_append(text_box.get("1.0", "end-1c"))
)
copy_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

# ------------------------------------------------------------------------------------
# Prediction & Hand Box Logic
# ----------------------------------------------------------------------------------
prediction_buffer = []
buffer_start_time = None
BUFFER_DURATION = 0.1
FLASH_DURATION = 0.2
capture_flash = False
flash_start_time = None
current_confidence = 0

PADDING = 20
BOX_THICKNESS = 3


def update_frame():
    global prediction_buffer, buffer_start_time, capture_flash, flash_start_time, current_confidence

    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    frame_bgr = cv2.flip(frame, 1)
    rgb_for_mediapipe = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_for_mediapipe)

    current_prediction = None
    hand_detected = False

    if results.multi_hand_landmarks:
        hand_detected = True
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = frame_bgr.shape
            xs = [lm.x for lm in hand_landmarks.landmark]
            ys = [lm.y for lm in hand_landmarks.landmark]
            x_min, x_max = int(min(xs) * w) - PADDING, int(max(xs) * w) + PADDING
            y_min, y_max = int(min(ys) * h) - PADDING, int(max(ys) * h) + PADDING
            x_min, y_min = max(0, x_min), max(0, y_min)
            x_max, y_max = min(w, x_max), min(h, y_max)

            if capture_flash and (time.time() - flash_start_time <= FLASH_DURATION):
                overlay = frame_bgr.copy()
                cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (139, 69, 19), -1)
                frame_bgr = cv2.addWeighted(overlay, 0.4, frame_bgr, 0.6, 0)
                cv2.putText(frame_bgr, "Recognized!", (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (139, 69, 19), 2)
            else:
                cv2.rectangle(frame_bgr, (x_min, y_min), (x_max, y_max), (139, 69, 19), BOX_THICKNESS)
                cv2.rectangle(frame_bgr, (x_min - 1, y_min - 1), (x_max + 1, y_max + 1), (139, 69, 19), 1)

            data = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten().reshape(1, -1)
            prediction = model.predict(data)[0]
            confidence = model.predict_proba(data).max()
            current_confidence = confidence

            if confidence > 0.3:
                current_prediction = prediction

    if hand_detected:
        status_label.configure(text="Detecting..." if not current_prediction else f"Sign: {current_prediction}")
        status_dot.configure(text_color="#fbbf24")
        confidence_value.configure(text=f"{current_confidence:.0%}")
        confidence_bar.set(current_confidence)
    else:
        status_label.configure(text="No hand detected")
        status_dot.configure(text_color="#ef4444")
        confidence_value.configure(text="--")
        confidence_bar.set(0)

    if current_prediction:
        if buffer_start_time is None:
            buffer_start_time = time.time()
            prediction_buffer = [current_prediction]
        elif time.time() - buffer_start_time >= BUFFER_DURATION:
            text_box.insert("end", prediction_buffer[0])
            text_box.see("end")
            capture_flash = True
            flash_start_time = time.time()
            status_label.configure(text="Recognized!")
            status_dot.configure(text_color="#10a37f")
            buffer_start_time = None
            prediction_buffer = []

    label_w = video_label.winfo_width()
    label_h = video_label.winfo_height()
    if label_w > 10 and label_h > 10:
        frame_h, frame_w, _ = frame_bgr.shape
        frame_aspect = frame_w / frame_h
        label_aspect = label_w / label_h

        if frame_aspect > label_aspect:
            new_h = label_h
            new_w = int(frame_aspect * new_h)
            frame_resized = cv2.resize(frame_bgr, (new_w, new_h))
            x_start = (new_w - label_w) // 2
            frame_bgr = frame_resized[:, x_start:x_start + label_w]
        else:
            new_w = label_w
            new_h = int(new_w / frame_aspect)
            frame_resized = cv2.resize(frame_bgr, (new_w, new_h))
            y_start = (new_h - label_h) // 2
            frame_bgr = frame_resized[y_start:y_start + label_h, :]

    frame_display = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_display)
    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(label_w, label_h))
    video_label.configure(image=ctk_img)
    video_label.image = ctk_img

    root.after(10, update_frame)


update_frame()
root.mainloop()