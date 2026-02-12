import psutil
import time
import threading
from datetime import datetime, timedelta

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
        
        # State tracking for smart notifications
        self.last_alerts = {}  # category -> timestamp
        self.alert_cooldown = 600  # 10 minutes cooldown for same alert
        self.battery_state = None  # Track battery state changes
        self.memory_state = "normal"  # normal, high, critical
        self.last_uptime_check = None
        
        # Thresholds
        self.battery_critical = 10
        self.battery_low = 20
        self.battery_energy_saver = 45
        self.battery_optimal = 95
        self.memory_high = 85
        self.memory_critical = 95
        self.cpu_high = 90
        self.uptime_reboot_days = 7

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
            self.thread.join(timeout=1.0)

    def _should_notify(self, category):
        """Check if enough time has passed since last notification of this category."""
        now = time.time()
        if category not in self.last_alerts:
            self.last_alerts[category] = now
            return True
        
        if now - self.last_alerts[category] > self.alert_cooldown:
            self.last_alerts[category] = now
            return True
        
        return False

    def _monitor_loop(self):
        """Main loop with smart polling intervals."""
        print("System Monitoring started...")
        battery_counter = 0
        memory_counter = 0
        
        while self.running:
            try:
                # Check memory every 30 minutes (1800 seconds)
                if memory_counter % 1800 == 0:
                    self._check_memory()
                
                # Check battery every 1 hour (3600 seconds)
                if battery_counter % 120 == 0:
                    self._check_battery()
                    battery_counter = 0
                
                # Check uptime once per day
                if memory_counter % 86400 == 0:  # Once per day
                    self._check_uptime()
                
                # Sleep 1 second and increment counters
                time.sleep(1)
                memory_counter += 1
                battery_counter += 1
                
                if not self.running:
                    break
                    
            except Exception as e:
                print(f"Monitor Error: {e}")
                time.sleep(60)

    def _check_battery(self):
        battery = psutil.sensors_battery()
        if not battery:
            return

        percent = int(battery.percent)
        plugged = battery.power_plugged
        
        # Create state key for detecting changes
        current_state = f"{percent}_{plugged}"
        
        # Only notify on state changes to avoid spam
        if self.battery_state == current_state:
            return
        
        self.battery_state = current_state
        
        # Critical battery (< 10%)
        if percent <= self.battery_critical and not plugged:
            if self._should_notify("battery_critical"):
                self.callback("Battery", f"Sir, your battery is critically low at {percent} percent. Please charge your laptop immediately.")
        
        # Low battery (< 20%)
        elif percent <= self.battery_low and not plugged:
            if self._should_notify("battery_low"):
                self.callback("Battery", f"Sir, battery is running low at {percent} percent. You might want to plug in the charger soon.")
        
        # Energy saver suggestion (< 45%)
        elif percent <= self.battery_energy_saver and not plugged:
            if self._should_notify("battery_energy_saver"):
                self.callback("Battery", f"Sir, battery is lower than {percent} percent. Please turn on energy saver mode.")
        
        # Optimal charge reached (>= 95%)
        elif percent >= self.battery_optimal and plugged:
            if self._should_notify("battery_full"):
                self.callback("Battery", f"Battery is at {percent} percent, sir. You can unplug the charger now to preserve battery health.")

    def _check_memory(self):
        mem = psutil.virtual_memory()
        percent = int(mem.percent)
        
        # Determine state
        if percent >= self.memory_critical:
            new_state = "critical"
        elif percent >= self.memory_high:
            new_state = "high"
        else:
            new_state = "normal"
        
        # Only notify on state changes
        if new_state == self.memory_state:
            return
        
        old_state = self.memory_state
        self.memory_state = new_state
        
        # Critical memory
        if new_state == "critical" and old_state != "critical":
            if self._should_notify("memory_critical"):
                self.callback("Memory", f"Sir, system memory is critically high at {percent} percent. You should close some applications immediately.")
        
        # High memory
        elif new_state == "high" and old_state == "normal":
            if self._should_notify("memory_high"):
                self.callback("Memory", f"Memory usage is getting high at {percent} percent, sir. Might want to check what's running.")


    def _check_uptime(self):
        """Check system uptime and suggest reboot if needed."""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        if uptime.days >= self.uptime_reboot_days:
            if self._should_notify("uptime_reboot"):
                self.callback("System", f"Your system has been running for {uptime.days} days, sir. Your laptop might need some rest. A reboot would help improve performance.")

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

    def get_top_memory_process(self):
        """Identify the process consuming the most memory."""
        try:
            # Get list of processes with memory info
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    pinfo = proc.info
                    if pinfo and pinfo.get('memory_info'):
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort by memory usage (rss)
            if not processes:
                return "I couldn't list the processes."
                
            top_process = sorted(processes, key=lambda p: p['memory_info'].rss, reverse=True)[0]
            
            # Convert bytes to MB/GB
            mem_usage_mb = top_process['memory_info'].rss / (1024 * 1024)
            if mem_usage_mb > 1024:
                mem_str = f"{mem_usage_mb/1024:.1f} GB"
            else:
                mem_str = f"{mem_usage_mb:.0f} MB"
                
            return f"The process using the most memory is {top_process['name']}, consuming {mem_str}."
            
        except Exception as e:
            return f"I failed to check process memory: {e}"
