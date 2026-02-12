# Running Jarvis on Android (Termux)

This guide explains how to set up Jarvis on your Android tablet using Termux.

## Prerequisites

1.  **F-Droid**: It is recommended to install Termux from F-Droid, not the Play Store (Play Store version is outdated).
2.  **Termux**: Terminal emulator.
3.  **Termux:API**: App add-on for hardware access (TTS, Audio, etc.).

## Installation Steps

### 1. Install Apps
1.  Download **F-Droid** from [f-droid.org](https://f-droid.org/).
2.  Install **Termux** from F-Droid.
3.  Install **Termux:API** from F-Droid.

### 2. Configure Termux
Open Termux and run the following commands to update and install packages:

```bash
pkg update && pkg upgrade -y
pkg install python git termux-api build-essential cmake -y
```

### 3. Grant Permissions
You need to grant Termux access to storage and microphone.
```bash
termux-setup-storage
termux-microphone-record
```
(Accept the permission prompts)

**IMPORTANT**: Open the **Termux:API** app once to ensure it's initialized, and ensure Termux has "run in background" and "display over other apps" permissions if possible for best performance.

### 4. Clone/Copy Jarvis
If you haven't already, clone the repo or copy your files to Termux.

```bash
cd ~
# If cloning from git
# git clone <your-repo-url> jarvisassistant
# cd jarvisassistant
```

### 5. Install Python Dependencies
Mac-specific libraries (`pyobjc`, `sounddevice` with PortAudio) might be tricky on Android. We use `vosk` which is supported.

**Note**: `sounddevice` / `pyaudio` often requires `portaudio`.
```bash
pkg install portaudio
pip install -r requirements.txt
```
If `sounddevice` fails, you might need: `pip install sounddevice` explicitly after installing portaudio.

### 6. Download Vosk Model
Jarvis needs a proper Vosk model to run offline.
```bash
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
rm vosk-model-small-en-us-0.15.zip
cd ..
```
*Note: You can use a larger model for better accuracy if your tablet has space/RAM.*

### 7. Run Jarvis
```bash
python main.py
```

## Known Limitations on Android
- **Porcupine (Wake Word)**: `pvporcupine` Python package might not allow the Mac access key or might need a different platform wheel. If `pvporcupine` fails, we might need a pure Vosk wake word approach or a different library.
    - *Fix*: You might need to `pip install pvporcupine` specifically for Linux/ARM if available, or use `vosk` for wake word detection too.
- **Microphone**: Ensure no other app is using the mic.
- **Background**: Android kills background processes. Use "Acquire Wakelock" from Termux notification to keep it running.
