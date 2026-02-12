# Jarvis AI Assistant (Offline Mode)

A fully offline, voice-activated AI assistant for macOS.

## Predetermined Features
- **Offline Wake Word**: Uses Porcupine to listen for "Jarvis".
- **Offline Voice Recognition**: Uses Vosk API.
- **Offline TTS**: Uses macOS built-in high-quality `say` command.
- **System Monitoring**: Checks Battery, RAM, CPU, Disk usage every 60s and warns you proactively.
- **Automation**: Opens apps, shuts down, restarts, tells time and system status.

---

## 1. Installation

### Prerequisites
- macOS
- Python 3.9+
- Homebrew (recommended)

### Step 1: Install Python Dependencies
**Note:** We use `sounddevice` which usually includes necessary binaries. No need for Homebrew or PortAudio system installation.

Navigate to the project folder and create a virtual environment:
```bash
cd /Users/prem/jarvisassistant
python3 -m venv venv
source venv/bin/activate
```

Install Python libraries:
```bash
pip install -r requirements.txt
```

### Step 3: Download Vosk Model
1. Go to [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Download a lightweight model like `vosk-model-small-en-us-0.15`.
3. Extract the downloaded zip.
4. Rename the extracted folder to `model`.
5. Move the `model` folder inside a `models` directory in this project.

Structure should look like:
```
jarvisassistant/
├── models/
│   └── model/  <-- Contains 'conf', 'graph', etc.
├── main.py
...
```

### Step 4: Get Porcupine Access Key (Free)
1. Sign up at [https://console.picovoice.ai/](https://console.picovoice.ai/)
2. Copy your `AccessKey`.
3. Open `main.py` and paste it into the `PORCUPINE_ACCESS_KEY` variable.

---

## 2. Usage

Run Jarvis manually to test:
```bash
source venv/bin/activate
python main.py
```
- Say **"Jarvis"**.
- Wait for response ("Yes?").
- Say a command:
  - "Open Calculator"
  - "Open Safari"
  - "System status"
  - "What time is it"
  - "Shutdown system"

---

## 3. Run in Background (Launchd)

To make Jarvis run automatically at login:

1. Edit the file `com.prem.jarvis.plist` (create it if missing) with the correct paths.
2. Copy it to LaunchAgents:
   ```bash
   cp com.prem.jarvis.plist ~/Library/LaunchAgents/
   ```
3. Load the service:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.prem.jarvis.plist
   ```
4. Jarvis will now start automatically on login.

To stop it:
```bash
launchctl unload ~/Library/LaunchAgents/com.prem.jarvis.plist
```
