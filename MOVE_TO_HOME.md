# Moving Jarvis to Home Directory - Step by Step

## Run These Commands in Order:

```bash
# 1. Move jarvisassistant from Desktop to home directory
mv /Users/prem/Desktop/jarvisassistant /Users/prem/jarvisassistant

# 2. Navigate to new location
cd /Users/prem/jarvisassistant

# 3. Remove the old autostart configuration
rm ~/Library/LaunchAgents/com.prem.jarvis.plist

# 4. Start Jarvis
python main.py
```

## After Python Starts:

1. Wait for "Jarvis is online"
2. Say: **"Jarvis, enable autostart"**
3. Wait for "Autostart enabled successfully"
4. Press `Ctrl+C` to stop
5. **Restart your Mac** (or log out and log back in)

## After Restart:

Jarvis should automatically start!

Test by saying **"Jarvis"** - you should hear the Tink sound! 🔊

---

## If You Need to Check Status:

```bash
# Check if running
ps aux | grep "python.*main.py" | grep -v grep

# Check logs
tail -20 /tmp/jarvis.err
tail -20 /tmp/jarvis.out
```

---

**Ready? Copy and paste the commands above into your terminal!**
