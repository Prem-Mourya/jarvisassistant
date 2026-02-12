import logging
import sys
import utils

def check_app_running(app_name):
    """Check if an app is currently running."""
    if utils.PLATFORM != "mac":
        return False
        
    try:
        # pgrep -x "Calculator"
        result = subprocess.run(["pgrep", "-x", app_name], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def open_app(app_name):
    """Open an application using utils.open_app."""
    return utils.open_app(app_name)

# Deprecated/Refactored: Old open_app impl removed in favor of utils.open_app
def _old_open_app_ref(app_name):
    """Open a macOS application using the 'open' command."""
    try:
        logging.info(f"Opening app: {app_name}")
        # -g = do not bring to foreground (background), but for user we want foreground.
        # -a = application
        res = subprocess.run(["open", "-a", app_name])
        if res.returncode != 0:
            logging.error(f"Failed to open {app_name}, return code: {res.returncode}")
            return False
        return True
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        return False

def close_app(app_name):
    """Close a macOS application using osascript (AppleScript) to quit gracefully."""
    if utils.PLATFORM != "mac":
        print(f"Closing apps not supported on {utils.PLATFORM}")
        return False

    try:
        script = f'tell application "{app_name}" to quit'
        subprocess.run(["osascript", "-e", script])
        return True
    except Exception as e:
        print(f"Error closing {app_name}: {e}")
        return False

def setup_autostart():
    """Create a Launch Agent to start Jarvis on login."""
    if utils.PLATFORM != "mac":
        print(f"Autostart setup not supported on {utils.PLATFORM} via this script.")
        # On Android, user should use Termux:Boot
        return False
    try:
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.prem.jarvis</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.join(os.getcwd(), 'main.py')}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/jarvis.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/jarvis.err</string>
</dict>
</plist>
"""
        home = os.path.expanduser("~")
        launch_agents_dir = os.path.join(home, "Library/LaunchAgents")
        if not os.path.exists(launch_agents_dir):
            os.makedirs(launch_agents_dir)
            
        plist_path = os.path.join(launch_agents_dir, "com.prem.jarvis.plist")
        
        with open(plist_path, "w") as f:
            f.write(plist_content)
            
        # Unload if exists then load
        subprocess.run(["launchctl", "unload", plist_path], capture_output=True)
        subprocess.run(["launchctl", "load", plist_path], capture_output=True)
        
        logging.info(f"Autostart enabled. Plist at: {plist_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to setup autostart: {e}")
        return False

def shutdown_system():
    """Shut down the system with a confirmation dialog (or immediately)."""
    if utils.PLATFORM != "mac":
        print("Shutdown not implemented for this platform.")
        return

    # Using 'osascript' to show a confirmation dialog is safer, but user asked for functionality.
    # We will use the standard shutdown command which usually requires sudo or user interaction.
    # A safer way without sudo is specific to user setup, but 'osascript' can tell Finder to shut down.
    try:
        script = 'tell application "System Events" to shut down'
        subprocess.run(["osascript", "-e", script])
    except Exception as e:
        print(f"Error shutting down: {e}")

def restart_system():
    """Restart the system."""
    if utils.PLATFORM != "mac":
        print("Restart not implemented for this platform.")
        return
    try:
        script = 'tell application "System Events" to restart'
        subprocess.run(["osascript", "-e", script])
    except Exception as e:
        print(f"Error restarting: {e}")

def get_system_uptime():
    """Get system uptime string."""
    try:
        result = subprocess.check_output("uptime", shell=True).decode("utf-8")
        # Format: 14:10  up 1 day,  3:18, 3 users, load averages: 1.41 1.49 1.35
        return result.split("up")[1].split(",")[0].strip()
    except Exception:
        return "Unknown"
