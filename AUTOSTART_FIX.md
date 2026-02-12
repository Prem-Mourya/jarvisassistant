# ⚠️ Autostart Issue: Permission Problem

## Problem Found!

The autostart service is failing with:
```
PermissionError: Operation not permitted: '/Users/prem/Desktop/jarvisassistant/venv/pyvenv.cfg'
```

**Why?** macOS LaunchAgents cannot access files in `~/Desktop` without **Full Disk Access** permission.

---

## 🔧 Solution Options

### **Option 1: Grant Full Disk Access to Python (Recommended)**

1. Open **System Preferences** (System Settings)
2. Go to **Privacy & Security** → **Full Disk Access**
3. Click the **lock icon** and enter your password
4. Click **"+"** button
5. Navigate to and add:
   ```
/Users/prem/Desktop/jarvisassistant/venv/bin/python
   ```
6. Restart the LaunchAgent:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.prem.jarvis.plist
   launchctl load ~/Library/LaunchAgents/com.prem.jarvis.plist
   ```

### **Option 2: Move Jarvis to Home Directory**

Move the entire project from Desktop to your home folder:

```bash
mv /Users/prem/Desktop/jarvisassistant /Users/prem/jarvisassistant
cd /Users/prem/jarvisassistant
python main.py
# Say "Jarvis, enable autostart" again
```

---

## ✅ How to Test After Fixing

1. Check if service is running:
   ```bash
   launchctl list | grep jarvis
   ```
   
2. Check for errors:
   ```bash
   tail -20 /tmp/jarvis.err
   ```

3. Test wake word:
   Say **"Jarvis"** - you should hear the Tink sound!

---

## Current Status

✅ Autostart plist created  
✅ LaunchAgent loaded  
❌ Permission denied accessing Desktop  
  
**Next step:** Choose Option 1 or

 Option 2 above to fix permissions.
