# 🚀 Jarvis Autostart Setup (One-Time Only)

Follow these steps **ONCE** to make Jarvis run automatically every time you boot your Mac:

## Setup Steps (Do This Once)

1. **Open Terminal** and navigate to Jarvis folder:
   ```bash
   cd /Users/prem/Desktop/jarvisassistant
   ```

2. **Start Jarvis**:
   ```bash
   python main.py
   ```

3. **Enable Autostart** (say this):
   > "Jarvis, enable autostart"
   
   Jarvis will respond: "Autostart enabled successfully"

4. **Done!** You can now close the Terminal.

## What Happens After Setup?

✅ **Every time you boot your Mac:**
- Jarvis starts automatically in the background
- Wake word detection is active
- System monitoring is running
- You don't need to open Terminal or run any commands

✅ **Jarvis stays running:**
- Until you logout
- Until you shutdown/restart your Mac
- Even if you close Terminal or other apps

## How to Use Jarvis After Setup

Just say **"Jarvis"** anytime and give your command!

No need to run `python main.py` ever again.

## To Disable Autostart (Optional)

If you ever want to disable autostart:

```bash
launchctl unload ~/Library/LaunchAgents/com.prem.jarvis.plist
rm ~/Library/LaunchAgents/com.prem.jarvis.plist
```

## Logs (If Needed)

If Jarvis isn't working, check the logs:
- Output: `/tmp/jarvis.out`
- Errors: `/tmp/jarvis.err`
