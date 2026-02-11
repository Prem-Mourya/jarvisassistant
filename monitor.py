import psutil
import time
import threading

class SystemMonitor:
    def __init__(self, callback):
        """
        Initialize System Monitor.
        :param callback: Function to call when an alert condition is met. 
                         Signature: callback(category, message)
        """
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_cpu_alert_time = 0

    def start(self):
        """Start the monitoring loop in a background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor_loop(self):
        """Main loop that checks system stats every 60 seconds."""
        print("System Monitoring started...")
        while self.running:
            try:
                self._check_battery()
                self._check_memory()
                self._check_disk()
                self._check_cpu()
                
                # Sleep for 60 seconds
                for _ in range(60):
                    if not self.running: 
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"Monitor Error: {e}")
                time.sleep(60)

    def _check_battery(self):
        battery = psutil.sensors_battery()
        if not battery:
            return

        percent = battery.percent
        plugged = battery.power_plugged

        # Rule: Battery > 85% and charging → suggest unplugging.
        if percent > 85 and plugged:
            self.callback("Battery", f"Battery is at {percent} percent and charging. You might want to unplug to preserve battery health.")
        
        # Rule: Battery < 20% → suggest charging.
        if percent < 20 and not plugged:
            self.callback("Battery", f"Battery is low at {percent} percent. Please connect the charger.")

    def _check_memory(self):
        mem = psutil.virtual_memory()
        # Rule: RAM > 85% → suggest closing heavy apps.
        if mem.percent > 85:
            self.callback("RAM", f"Memory usage is high at {mem.percent} percent. Consider closing unused applications.")

    def _check_disk(self):
        disk = psutil.disk_usage('/')
        # Rule: Disk almost full (>90%) → suggest cleaning storage.
        if disk.percent > 90:
            self.callback("Disk", f"Disk storage is {disk.percent} percent full. You should clean up some files.")

    def _check_cpu(self):
        # Rule: CPU > 90% for more than 30 seconds.
        # This is a simplified check: if it's high now, we wait 30s and check again.
        if psutil.cpu_percent(interval=1) > 90:
            time.sleep(30)
            if psutil.cpu_percent(interval=1) > 90:
                # Avoid spamming (simple debounce)
                if time.time() - self.last_cpu_alert_time > 300: # 5 min cooldown
                    self.last_cpu_alert_time = time.time()
                    self.callback("CPU", "CPU usage has been high for over 30 seconds. You might want to check Activity Monitor.")

    def get_status_summary(self):
        """Return a string summary of current system status."""
        battery = psutil.sensors_battery()
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        batt_str = f"{battery.percent}%" if battery else "Unknown"
        plugged_str = "Charging" if battery and battery.power_plugged else "On Battery"
        
        return (f"Battery is at {batt_str} and {plugged_str}. "
                f"Memory usage is {mem.percent}%. "
                f"CPU usage is around {cpu}%.")
