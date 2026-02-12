# Running Jarvis on Android (Termux)

This guide explains how to set up Jarvis on your Android tablet using Termux.

## Prerequisites

1.  **F-Droid**: It is recommended to install Termux from F-Droid.
2.  **Termux**: Terminal emulator.
3.  **Termux:API**: App add-on.

## Installation Steps (Updated for Dependency Fixes)

### 1. Install System Packages
Open Termux and run:

```bash
pkg update && pkg upgrade -y
# Install build tools and python
pkg install python git termux-api build-essential cmake libffi openssl -y
```

### 2. Grant Permissions
```bash
termux-setup-storage
termux-microphone-record
```
**IMPORTANT**: Open the **Termux:API** app once to initialize it.

### 3. Copy Jarvis Config
Copy the `jarvisassistant` folder to your tablet (e.g., via USB or `git clone`).
```bash
cd ~/jarvisassistant
```

### 4. Install Python Dependencies (Android Specific)
We use a special requirements file for Android to avoid Mac-only packages and broken wake-word engines.

```bash
# Update pip first
pip install --upgrade pip

# Install dependencies (ignoring pvporcupine/vosk for a moment to ensure base works)
pip install -r requirements_android.txt
```

**Troubleshooting Vosk**:
If `pip install vosk` fails with "No matching distribution":
1.  Try: `pip install vosk==0.3.45` (sometimes newer versions miss wheels).
2.  Or: `pip install https://github.com/alphacephei/vosk-api/releases/download/v0.3.50/vosk-0.3.50-py3-none-any.whl` (if available).
3.  Usually `pip install vosk` works if `libffi` and `build-essential` are installed and `pip` is updated.
4. Try installing `wheel` first: `pip install wheel`.

### 5. Download HIGH ACCURATE Vosk Model
Since your tablet has good RAM, use the large model for best accuracy.

```bash
mkdir -p models
cd models

# Downloading the BIG model (approx 1.8GB) - accurate!
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
mv vosk-model-en-us-0.22 model
rm vosk-model-en-us-0.22.zip

cd ..
```

### 6. Run Jarvis
```bash
python main.py
```
*Note: Without `pvporcupine`, Jarvis will start in "Always Listening" mode or immediately try to process speech. Watch the output.*

## Tips
- **Wake Lock**: Notification -> Acquire Wakelock.
- **TTS**: Ensure Google Text-to-Speech engine is installed on Android for `termux-tts-speak` to sound good.
