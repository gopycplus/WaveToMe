import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import json

# ---------------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------------
SPLASH_W, SPLASH_H = 500, 380
APP_W, APP_H = 900, 600
SPLASH_DURATION_MS = 4000
ASSETS_DIR = "assets"
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
SETTINGS_FILE = "settings.json"

# Language list
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese": "zh",
    "Arabic": "ar",
    "Hindi": "hi",
    "Uzbek": "uz"
}

# ------------------------------------------------------------------------------------------
# CTk Theme
# -----------------------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ------------------------------------------------------------------------------------------
# Settings Persistence
# ---------------------------------------------------------------------------------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "language": "English",
        "language_code": "en",
        "gender": "Male",
        "speed": 3.0
    }


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


def show_splash(parent):
    splash = tk.Toplevel(parent)
    splash.overrideredirect(True)
    splash.configure(bg="#0f1419")
    center_window(splash, SPLASH_W, SPLASH_H)

    # Main dark container
    container = tk.Frame(splash, bg="#0f1419", bd=0, relief="flat")
    container.place(relx=0, rely=0, width=SPLASH_W, height=SPLASH_H)

    # Top section with logo
    top_section = tk.Frame(container, bg="#0f1419")
    top_section.place(relx=0.5, rely=0.35, anchor="center")

    # Logo
    if os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH)
            img.thumbnail((240, 160), Image.LANCZOS)
            logo_imgtk = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(top_section, image=logo_imgtk, bg="#0f1419")
            lbl_logo.image = logo_imgtk
            lbl_logo.pack(pady=(50, 0))
        except Exception:
            pass

    # Label
    lbl_name = tk.Label(
        top_section, text="WaveToMe",
        font=("Segoe UI", 32, "bold"),
        fg="#4a9eff", bg="#0f1419"
    )
    lbl_name.pack(pady=(15, 0))

    # Bottom section
    bottom_section = tk.Frame(container, bg="#0f1419")
    bottom_section.place(relx=0.5, rely=0.85, anchor="center")

    # Loading bar background
    loading_bg = tk.Frame(bottom_section, bg="#2d2d2d", width=200, height=3)
    loading_bg.pack()

    # Loading bar (animated)
    loading_bar = tk.Frame(loading_bg, bg="#0078d4", width=0, height=3)
    loading_bar.place(x=0, y=0)

    def animate_loading(width=0):
        if width <= 200:
            loading_bar.config(width=width)
            splash.after(20, animate_loading, width + 2)

    animate_loading()

    # Version
    version_text = tk.Label(
        bottom_section, text="Version 1.0",
        font=("Segoe UI", 9),
        fg="#8a8a8a", bg="#0f1419"
    )
    version_text.pack(pady=(10, 5))

    copyright_text = tk.Label(
        bottom_section, text="© 2025 WaveToMe. All rights reserved.",
        font=("Segoe UI", 8),
        fg="#6a6a6a", bg="#0f1419"
    )
    copyright_text.pack()

    parent.after(SPLASH_DURATION_MS, lambda: close_splash_and_start(parent, splash))

def close_splash_and_start(root, splash):
    try:
        splash.destroy()
    except Exception:
        pass
    start_landing_page(root)


# -------------------------------------------------------------------------------------------------------------------
# Settings Window
# -------------------------------------------------------------------------------------------
def open_settings(root):
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


# ----------------------------------------------------------------------------------------------
# Landing Page
# ---------------------------------------------------------------------------------
def start_landing_page(root):
    root.deiconify()
    root.title("WaveToMe - Sign Language Recognition")
    root.resizable(False, False)

    if os.path.exists(ICON_PATH):
        try:
            root.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"Error loading icon: {e}")

    center_window(root, APP_W, APP_H)

    for child in root.winfo_children():
        child.destroy()

    root.configure(fg_color="#0f1419")

    # Left panel - Hero section
    left_panel = ctk.CTkFrame(root, fg_color="#1a1f2e", corner_radius=0, width=500)
    left_panel.pack(side="left", fill="both", expand=True)
    left_panel.pack_propagate(False)

    # Hero content
    hero_container = ctk.CTkFrame(left_panel, fg_color="transparent")
    hero_container.place(relx=0.5, rely=0.45, anchor="center")

    # Logo placeholder or icon
    logo_frame = ctk.CTkFrame(hero_container, fg_color="#1a1f2e", corner_radius=20, width=210, height=140)
    logo_frame.pack(pady=(25, 25))
    logo_frame.pack_propagate(False)

    if os.path.exists(LOGO_PATH):
        try:
            img = Image.open(LOGO_PATH)
            img.thumbnail((210, 140), Image.LANCZOS)
            logo_imgtk = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(logo_frame, image=logo_imgtk, bg="#1a1f2e")
            lbl_logo.image = logo_imgtk
            lbl_logo.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            logo_text = ctk.CTkLabel(logo_frame, text="WAVE", font=("Segoe UI", 18, "bold"), text_color="#4a9eff")
            logo_text.place(relx=0.5, rely=0.5, anchor="center")

    title_label = ctk.CTkLabel(hero_container, text="WaveToMe",
                               font=("Segoe UI", 48, "bold"), text_color="#4a9eff")
    title_label.pack()

    subtitle_label = ctk.CTkLabel(hero_container,
                                  text="Regain Your Voice",
                                  font=("Segoe UI", 18), text_color="#8fa0b0")
    subtitle_label.pack(pady=(8, 5))

    description_label = ctk.CTkLabel(hero_container,
                                     text="Real-time sign language recognition\npowered by advanced AI",
                                     font=("Segoe UI", 13), text_color="#6080a0", justify="center")
    description_label.pack(pady=(0, 20))

    # Features list
    features_frame = ctk.CTkFrame(hero_container, fg_color="transparent")
    features_frame.pack(pady=(10, 0))

    features = [
        ("Real-time Detection", "#4a9eff"),
        ("Multi-language Support", "#10a37f"),
        ("Text-to-Speech", "#f59e0b")
    ]

    for feature, color in features:
        feature_item = ctk.CTkFrame(features_frame, fg_color="#242933", corner_radius=8, height=35)
        feature_item.pack(fill="x", pady=3, padx=20)

        dot = ctk.CTkLabel(feature_item, text="●", font=("Segoe UI", 16), text_color=color)
        dot.pack(side="left", padx=(12, 8))

        label = ctk.CTkLabel(feature_item, text=feature, font=("Segoe UI", 12), text_color="#d0d8e0")
        label.pack(side="left", pady=6, padx=(0, 20))

    # Right panel - Actions
    right_panel = ctk.CTkFrame(root, fg_color="#0f1419", corner_radius=0)
    right_panel.pack(side="right", fill="both", expand=True, padx=40, pady=60)

    action_container = ctk.CTkFrame(right_panel, fg_color="transparent")
    action_container.place(relx=0.5, rely=0.5, anchor="center")

    welcome_label = ctk.CTkLabel(action_container,
                                 text="Get Started",
                                 font=("Segoe UI", 32, "bold"), text_color="#ffffff")
    welcome_label.pack(pady=(0, 15))

    instruction_label = ctk.CTkLabel(action_container,
                                     text="Launch the recognition system\nand start communicating",
                                     font=("Segoe UI", 14), text_color="#8fa0b0", justify="center")
    instruction_label.pack(pady=(0, 35))

    def start_recognition():
        try:
            root.destroy()
            subprocess.Popen([sys.executable, "main.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not start recognition:\n{e}")

    def show_instructions():
        instructions = (
            "Instructions:\n\n"
            "1. Click 'Start Recognition' to launch the camera.\n"
            "2. Ensure your hand is visible in the webcam.\n"
            "3. The recognized sign will appear in the textbox.\n"
            "4. Use 'Settings' to configure preferences."
        )
        messagebox.showinfo("Instructions", instructions)

    # Primary button
    btn_start = ctk.CTkButton(action_container, text="Start Recognition",
                              width=260, height=65, corner_radius=12,
                              fg_color="#4a9eff", hover_color="#357abd",
                              font=("Segoe UI", 18, "bold"), command=start_recognition)
    btn_start.pack(pady=(0, 15))

    # Secondary actions
    secondary_frame = ctk.CTkFrame(action_container, fg_color="transparent")
    secondary_frame.pack()

    btn_settings = ctk.CTkButton(secondary_frame, text="Settings",
                                 width=125, height=50, corner_radius=10,
                                 fg_color="#2a3f5f", hover_color="#3a4f6f",
                                 font=("Segoe UI", 14),
                                 command=lambda: open_settings(root))
    btn_settings.pack(side="left", padx=(0, 10))

    btn_instructions = ctk.CTkButton(secondary_frame, text="Instructions",
                                     width=125, height=50, corner_radius=10,
                                     fg_color="#2a3f5f", hover_color="#3a4f6f",
                                     font=("Segoe UI", 14), command=show_instructions)
    btn_instructions.pack(side="left")

    # Info card at bottom
    info_card = ctk.CTkFrame(action_container, fg_color="#1a1f2e", corner_radius=12, border_width=1,
                             border_color="#2a3f5f")
    info_card.pack(pady=(35, 0), padx=10)

    info_text = ctk.CTkLabel(info_card,
                             text="Tip: For best results, ensure good lighting\nand clear hand visibility",
                             font=("Segoe UI", 11), text_color="#6080a0", justify="center")
    info_text.pack(padx=20, pady=15)


# ------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    root.configure(fg_color="#0f1419")
    show_splash(root)
    root.mainloop()