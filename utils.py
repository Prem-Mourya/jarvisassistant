import sys
import subprocess
import os
import logging
import platform

def get_platform():
    """
    Detect the current platform.
    Returns: 'mac', 'android', 'linux', or 'unknown'
    """
    system = platform.system().lower()
    
    # Check for Android/Termux specifically
    if "com.termux" in os.environ.get("PREFIX", ""):
        return "android"
    
    if system == "darwin":
        return "mac"
    elif system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

PLATFORM = get_platform()

def speak(text):
    """
    Speak text using platform-specific TTS.
    Returns the subprocess.Popen object (or None) to allow stopping.
    """
    if not text:
        return None
        
    try:
        if PLATFORM == "mac":
            return subprocess.Popen(
                ["say", "-v", "Samantha", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif PLATFORM == "android":
            # Termux:API must be installed
            return subprocess.Popen(
                ["termux-tts-speak", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif PLATFORM == "linux":
            # Try espeak or spd-say
            if subprocess.run(["which", "espeak"], capture_output=True).returncode == 0:
                 return subprocess.Popen(
                    ["espeak", text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                 return subprocess.Popen(
                    ["spd-say", text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        else:
            print(f"TTS not supported on {PLATFORM}: {text}")
            return None
            
    except Exception as e:
        logging.error(f"Error in speak(): {e}")
        return None

def play_sound(sound_path):
    """
    Play a sound file.
    """
    if not os.path.exists(sound_path) and not sound_path.startswith("/System"):
         # On Mac /System sounds exist, but on Android they won't.
         # For now, just log if missing, or use a beep.
         if PLATFORM != "mac":
             logging.warning(f"Sound file not found: {sound_path}")
             return

    try:
        if PLATFORM == "mac":
            subprocess.run(["afplay", sound_path], check=False)
        elif PLATFORM == "android":
            # Try termux-media-player first, then play-audio
            if subprocess.run(["which", "termux-media-player"], capture_output=True).returncode == 0:
                 subprocess.run(["termux-media-player", "play", sound_path], check=False)
            else:
                 subprocess.run(["play-audio", sound_path], check=False)
        elif PLATFORM == "linux":
            subprocess.run(["aplay", sound_path], check=False)
            
    except Exception as e:
        logging.error(f"Error playing sound: {e}")

def open_url(url):
    """
    Open a URL in the default browser.
    """
    try:
        if PLATFORM == "mac":
            subprocess.run(["open", url], check=False)
        elif PLATFORM == "android":
             subprocess.run(["termux-open-url", url], check=False)
        elif PLATFORM == "linux":
             subprocess.run(["xdg-open", url], check=False)
        else:
             import webbrowser
             webbrowser.open(url)
    except Exception as e:
        logging.error(f"Error opening URL: {e}")

def open_app(app_name):
    """
    Launch an application.
    """
    try:
        if PLATFORM == "mac":
             subprocess.run(["open", "-a", app_name], check=False)
        elif PLATFORM == "android":
             # On Android we can try to launch by package name if we knew it, 
             # or just search via termux-open if it supports it? 
             # For now, just warn it's not fully supported.
             print(f"Opening apps by name '{app_name}' is not fully supported on Android yet.")
             # Try termux-open just in case it handles some intents
             # subprocess.run(["termux-open", app_name], check=False) 
        else:
             print(f"Open app not supported on {PLATFORM}")
    except Exception as e:
        logging.error(f"Error opening app: {e}")
