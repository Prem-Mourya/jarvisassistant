import subprocess
import os

def check_app_running(app_name):
    """Check if an app is currently running."""
    try:
        # pgrep -x "Calculator"
        result = subprocess.run(["pgrep", "-x", app_name], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def open_app(app_name):
    """Open a macOS application using the 'open' command."""
    try:
        subprocess.run(["open", "-a", app_name])
        return True
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        return False

def close_app(app_name):
    """Close a macOS application using osascript (AppleScript) to quit gracefully."""
    try:
        script = f'tell application "{app_name}" to quit'
        subprocess.run(["osascript", "-e", script])
        return True
    except Exception as e:
        print(f"Error closing {app_name}: {e}")
        return False

def shutdown_system():
    """Shut down the system with a confirmation dialog (or immediately)."""
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
