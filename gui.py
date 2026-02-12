import webview
import threading
import sys
import queue
import time
import json
import logging
import pvporcupine
import os

# Import Jarvis App
# Ensure main.py is in path or same directory
try:
    from main import JarvisApp, WAKE_WORD, PORCUPINE_ACCESS_KEY
except ImportError:
    # Fallback for when running in different context
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from main import JarvisApp, WAKE_WORD, PORCUPINE_ACCESS_KEY

# HTML Content
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis AI</title>
    <style>
        :root {
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-primary: #ffffff;
            --text-secondary: #b3b3b3;
            --accent: #00f2ff;
            --accent-glow: rgba(0, 242, 255, 0.3);
            --danger: #ff4757;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
            -webkit-user-select: none;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .title {
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
            background: linear-gradient(90deg, #fff, var(--text-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        
        .status-badge {
            background-color: var(--card-bg);
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid #333;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #555;
            transition: all 0.3s ease;
        }
        
        .status-dot.online {
            background-color: #2ecc71;
            box-shadow: 0 0 8px #2ecc71;
        }
        
        .status-dot.listening {
            background-color: var(--accent);
            animation: pulse-dot 1.5s infinite;
        }
        
        .status-dot.processing {
            background-color: #f1c40f;
        }
        
        @keyframes pulse-dot {
            0% { box-shadow: 0 0 0 0 var(--accent-glow); }
            70% { box-shadow: 0 0 0 8px transparent; }
            100% { box-shadow: 0 0 0 0 transparent; }
        }
        
        /* SIRI VISUALIZER CONTAINER */
        .siri-container {
            width: 140px;
            height: 140px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px auto;
            position: relative;
            transform: scale(0.8);
            transition: all 0.5s ease;
            opacity: 0.6;
        }
        
        .siri-container.active {
            transform: scale(1.1);
            opacity: 1;
        }
        
        /* THE BLOB */
        .siri-blob {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #00C6FF, #0072FF, #FF007F, #6A0DAD);
            background-size: 300% 300%;
            border-radius: 42% 58% 70% 30% / 45% 45% 55% 55%;
            animation: 
                morph 8s ease-in-out infinite both alternate,
                gradient-shift 10s ease infinite;
            filter: blur(8px);
            box-shadow: 
                0 0 40px rgba(0, 114, 255, 0.4),
                inset 0 0 20px rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            opacity: 0.8;
        }

        /* ACTIVE STATE ANIMATIONS */
        .siri-container.active .siri-blob {
            animation: 
                morph 3s ease-in-out infinite both alternate,
                gradient-shift 4s ease infinite,
                breathe 2s ease-in-out infinite;
            filter: blur(5px);
            box-shadow: 
                0 0 60px rgba(0, 198, 255, 0.6),
                inset 0 0 30px rgba(255, 255, 255, 0.4);
            opacity: 1;
        }
        
        /* LISTENING STATE (Faster) */
        .siri-container.listening .siri-blob {
            animation: 
                morph 1.5s ease-in-out infinite both alternate,
                gradient-shift 2s ease infinite;
            transform: scale(1.05);
        }

        @keyframes morph {
            0% { border-radius: 42% 58% 70% 30% / 45% 45% 55% 55%; transform: rotate(0deg); }
            25% { border-radius: 30% 70% 50% 50% / 50% 40% 60% 50%; }
            50% { border-radius: 60% 40% 30% 70% / 60% 50% 50% 40%; transform: rotate(180deg); }
            75% { border-radius: 50% 50% 70% 30% / 40% 60% 40% 60%; }
            100% { border-radius: 42% 58% 70% 30% / 45% 45% 55% 55%; transform: rotate(360deg); }
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        @keyframes breathe {
            0% { transform: scale(0.95); }
            50% { transform: scale(1.05); }
            100% { transform: scale(0.95); }
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .btn {
            background-color: var(--card-bg);
            color: var(--text-primary);
            border: 1px solid #333;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            border-color: var(--accent);
            background-color: #252525;
            transform: translateY(-1px);
        }
        
        .btn:active {
            transform: translateY(1px);
        }
        
        .btn.start {
            border-color: var(--accent);
            color: var(--accent);
        }
        
        .btn.start:hover {
            background-color: rgba(0, 242, 255, 0.1);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        .btn.stop {
            border-color: var(--danger);
            color: var(--danger);
        }
        
        .btn.stop:hover {
            background-color: rgba(255, 71, 87, 0.1);
            box-shadow: 0 0 15px rgba(255, 71, 87, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
            border-color: #333;
        }

        .console-container {
            flex: 1;
            background-color: var(--card-bg);
            border-radius: 12px;
            border: 1px solid #333;
            padding: 15px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            line-height: 1.5;
            display: flex;
            flex-direction: column;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
        }
        
        .log-entry {
            margin-bottom: 4px;
            word-break: break-word;
        }
        
        .log-time {
            color: #666;
            margin-right: 8px;
            font-size: 11px;
        }
        
        .log-info { color: #a4b0be; }
        .log-warn { color: #f1c40f; }
        .log-error { color: #ff4757; }
        .log-success { color: #2ecc71; }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0,0,0,0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #444;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Jarvis</div>
        <div class="status-badge">
            <div id="statusDot" class="status-dot"></div>
            <span id="statusText">Offline</span>
        </div>
    </div>
    
    <!-- SIRI VISUALIZER -->
    <div class="siri-container" id="visualizer">
        <div class="siri-blob"></div>
    </div>
    
    <div class="controls">
        <button id="btnStart" class="btn start" onclick="startJarvis()">Start System</button>
        <button id="btnStop" class="btn stop" onclick="stopJarvis()" disabled>Shutdown</button>
    </div>
    
    <div class="console-container" id="consoleLog">
        <div class="log-entry"><span class="log-time">SYSTEM</span> <span class="log-info">Interface initialized. Ready.</span></div>
    </div>

    <script>
        // Log handler
        function addLog(message, type='info') {
            const container = document.getElementById('consoleLog');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            
            const time = new Date().toLocaleTimeString().split(' ')[0];
            
            let colorClass = 'log-info';
            if (message.toLowerCase().includes('error') || type === 'error') colorClass = 'log-error';
            else if (message.toLowerCase().includes('warn') || type === 'warn') colorClass = 'log-warn';
            else if (message.toLowerCase().includes('success') || message.toLowerCase().includes('detected')) colorClass = 'log-success';
            
            entry.innerHTML = `<span class="log-time">${time}</span> <span class="${colorClass}">${message}</span>`;
            
            container.appendChild(entry);
            container.scrollTop = container.scrollHeight;
        }
        
        // Python interoperability
        function startJarvis() {
            pywebview.api.start().then(() => {
                document.getElementById('btnStart').disabled = true;
                document.getElementById('btnStop').disabled = false;
                updateStatus('Online', 'online');
                addLog('System starting...', 'info');
                document.getElementById('visualizer').classList.add('active');
            });
        }
        
        function stopJarvis() {
            pywebview.api.stop().then(() => {
                document.getElementById('btnStart').disabled = false;
                document.getElementById('btnStop').disabled = true;
                updateStatus('Offline', '');
                addLog('System stopped.', 'warn');
                document.getElementById('visualizer').classList.remove('active');
                document.getElementById('visualizer').classList.remove('listening');
            });
        }
        
        function updateStatus(text, className) {
            const dot = document.getElementById('statusDot');
            const label = document.getElementById('statusText');
            
            dot.className = 'status-dot ' + className;
            label.innerText = text;
        }
        
        // Polling for logs from Python
        setInterval(() => {
            if (window.pywebview) {
                pywebview.api.poll_logs().then((logs) => {
                    if (logs && logs.length > 0) {
                        logs.forEach(log => {
                            addLog(log);
                            const visualizer = document.getElementById('visualizer');
                            // Keyword detection for visual states
                            if (log.includes("Listening")) {
                                updateStatus('Listening', 'listening');
                                visualizer.classList.add('listening');
                            }
                            else if (log.includes("Wake word")) {
                                updateStatus('Active', 'processing');
                                visualizer.classList.add('active');
                            }
                            else if (log.includes("Processing")) {
                                updateStatus('Processing', 'processing');
                                visualizer.classList.remove('listening');
                                visualizer.classList.add('active');
                            }
                            else if (log.includes("Ready")) {
                                updateStatus('Online', 'online');
                                visualizer.classList.remove('listening');
                                visualizer.classList.add('active');
                            }
                            else if (log.includes("Waiting")) {
                                visualizer.classList.remove('listening');
                            }
                        });
                    }
                });
            }
        }, 500);
        
    </script>
</body>
</html>
"""

class JarvisAPI:
    def __init__(self):
        self.app_thread = None
        self.jarvis_app = None
        self.running = False
        self.log_queue = queue.Queue()
        
        # Redirect clean logs to our queue
        self.original_stdout = sys.stdout
        sys.stdout = self
        
    def write(self, text):
        if text.strip():
            self.log_queue.put(text.strip())
        self.original_stdout.write(text) # Also print to terminal
        
    def flush(self):
        self.original_stdout.flush()

    def start(self):
        if self.running:
            return
        
        self.running = True
        self.app_thread = threading.Thread(target=self._run_jarvis, daemon=True)
        self.app_thread.start()
        return True

    def stop(self):
        if self.jarvis_app:
            self.jarvis_app.stop()
        self.running = False
        return True
        
    def poll_logs(self):
        logs = []
        try:
            while True:
                log = self.log_queue.get_nowait()
                logs.append(log)
        except queue.Empty:
            pass
        return logs

    def _run_jarvis(self):
        try:
            self.jarvis_app = JarvisApp()
            # Initialize porcupine here in the thread
            self.jarvis_app.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=["jarvis"]
            )
            self.jarvis_app.monitor.start()
            
            print("Jarvis initialized successfully.")
            self.jarvis_app.voice.speak("System online.")
            
            self.jarvis_app.run_loop()
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self._cleanup()
            
    def _cleanup(self):
        if self.jarvis_app:
            self.jarvis_app.monitor.stop()
            if self.jarvis_app.porcupine:
                self.jarvis_app.porcupine.delete()
        print("Jarvis shutdown complete.")

def run_gui():
    api = JarvisAPI()
    window = webview.create_window(
        'Jarvis AI Assistant', 
        html=HTML,
        js_api=api,
        width=800,
        height=600,
        background_color='#121212',
        resizable=True
    )
    webview.start(debug=False)

if __name__ == '__main__':
    run_gui()
