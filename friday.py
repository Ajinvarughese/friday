import speech_recognition as sr
import subprocess
import psutil
import os
import pygame
import threading
import sys

import pystray
from pystray import MenuItem as item
from PIL import Image
import random

# ================= CONFIG =================
VOICE = random.choice(["SAGE", "CLOVE"])

WAKE_WORDS = ["friday", "hey friday", "sabine"]

OPEN_PHRASES = [
    "start my workspace",
    "open my environment",
    "let's begin",
    "wake up",
    "time to create",
    "time to work",
    "gotta work",
    "let's get to work",
    "let's start the work",
    "time to code"
]

CLOSE_PHRASES = [
    "close everything",
    "shut everything down",
    "end session",
    "wrap it up",
    "wrap things up"
]


APPS_TO_OPEN = [
    # [r"D:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2025.2.4\bin\idea64.exe"],
    [r"C:\Users\ajinv\AppData\Local\Programs\Microsoft VS Code\Code.exe"],
    [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "https://chat.openai.com"
    ],
    ["cmd", "/c", "start", "spotify"]   
]

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS  # PyInstaller temp folder
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()

BEGIN_VOICE = os.path.join(BASE_DIR, "audio", VOICE, f"{VOICE}_BEGIN.mp3")
START_VOICE = os.path.join(BASE_DIR, "audio", VOICE, f"{VOICE}_START.mp3")
END_VOICE = os.path.join(BASE_DIR, "audio", VOICE, f"{VOICE}_END.mp3")
ICON_PATH = os.path.join(BASE_DIR, "icon.png")


# =========================================

running = True
listening_enabled = True


def play_voice(file):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except Exception:
        pass


def open_apps():
    for app in APPS_TO_OPEN:
        try:
            subprocess.Popen(app)
        except Exception:
            pass


def close_apps():
    exe_names = {os.path.basename(app[0]).lower() for app in APPS_TO_OPEN}

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in exe_names:
                proc.terminate()
        except Exception:
            pass


def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio).lower()
    except Exception:
        return ""


def assistant_loop():
    global running, listening_enabled
    is_awake = False
    print(VOICE)

    while running:
        if not listening_enabled:
            continue

        try:
            command = listen_command()
            if not is_awake and any(w in command for w in WAKE_WORDS):
                play_voice(BEGIN_VOICE)
                is_awake = True
                continue

            if is_awake:
                if any(phrase in command for phrase in OPEN_PHRASES):
                    play_voice(START_VOICE)
                    open_apps()
                    is_awake = False

                elif any(phrase in command for phrase in CLOSE_PHRASES):
                    play_voice(END_VOICE)
                    close_apps()
                    is_awake = False

        except Exception:
            pass


# ================= TRAY =================

def load_tray_icon():
    return Image.open(ICON_PATH)


def toggle_listening(icon, item):
    global listening_enabled
    listening_enabled = not listening_enabled

def exit_app(icon, item):
    global running
    running = False
    icon.stop()
    sys.exit(0)

# ================= MAIN =================

if __name__ == "__main__":
    assistant_thread = threading.Thread(target=assistant_loop, daemon=True)
    assistant_thread.start()

    tray_icon = pystray.Icon(
        "Friday",
        load_tray_icon(),
        "Friday Assistant",
        menu=pystray.Menu(
            item("Pause / Resume", toggle_listening),
            item("Exit", exit_app),
        )
    )

    tray_icon.run()
