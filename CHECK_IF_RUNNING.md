# How to Check if Jarvis is Running

## Method 1: Quick Check (Terminal Command)

```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**If Jarvis is running**, you'll see output like:
```
prem  12345  2.0  1.5  /path/to/python /Users/prem/Desktop/jarvisassistant/main.py
```

**If nothing appears**, Jarvis is NOT running.

---

## Method 2: Activity Monitor (GUI)

1. Open **Activity Monitor** (Cmd+Space, type "Activity Monitor")
2. In the search box (top right), type: `python`
3. Look for a process running `main.py`
4. If you see it, Jarvis is running!

---

## Method 3: Test with Wake Word

Simply say **"Jarvis"** out loud:
- 🔊 **Hear a "Tink" sound?** → Jarvis is listening!
- 🔇 **No response?** → Jarvis is not running

---

## To View Logs (When Running as Background Service)

```bash
# View output
tail -f /tmp/jarvis.out

# View errors
tail -f /tmp/jarvis.err
```

Press `Ctrl+C` to stop viewing logs.

---

## To Stop Jarvis (Background Service)

If you want to manually stop the background service:

```bash
launchctl unload ~/Library/LaunchAgents/com.prem.jarvis.plist
```

To start it again:

```bash
launchctl load ~/Library/LaunchAgents/com.prem.jarvis.plist
```

---

## New Feature: Wake Sound! 🔊

When you say "Jarvis", you'll now hear a **"Tink" sound** to confirm Jarvis heard you and is listening for your command!
