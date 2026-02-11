import pvporcupine
import struct
import struct
import queue
import sounddevice as sd
import time
import logging
import threading
import sys

# Local imports
from voice import VoiceEngine
from monitor import SystemMonitor
import automation

# --- Configuration ---
# Get your FREE AccessKey from https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = "lJNt7xoOq7FnbPEcxej/ErPNuh/8+5VUduG3a3+sbeR5DrqCHjj/hg==" 

# Setup Logging
logging.basicConfig(filename='jarvis.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class JarvisApp:
    def __init__(self):
        self.voice = VoiceEngine()
        self.monitor = SystemMonitor(self.handle_monitor_alert)
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        
    def handle_monitor_alert(self, category, message):
        """Callback for system monitor to speak alerts."""
        logging.info(f"Monitor Alert [{category}]: {message}")
        # We need to be careful not to interrupt if user is speaking, 
        # but for simplicity, we just speak it.
        # Ideally, check if not 'listening' state.
        self.voice.speak(message)

    def process_command(self, command):
        """Process the text command received from Voice Engine."""
        cmd = command.lower()
        logging.info(f"Command received: {cmd}")
        
        if "time" in cmd:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            self.voice.speak(f"It is currently {now}")
            
        elif "status" in cmd or "system" in cmd:
            summary = self.monitor.get_status_summary()
            self.voice.speak(summary)
            
        elif "calculator" in cmd:
            self.voice.speak("Opening Calculator")
            automation.open_app("Calculator")
            
        elif "safari" in cmd:
            self.voice.speak("Opening Safari")
            automation.open_app("Safari")
            
        elif "activity monitor" in cmd:
            self.voice.speak("Opening Activity Monitor")
            automation.open_app("Activity Monitor")
            
        elif "finder" in cmd:
            self.voice.speak("Opening Finder")
            automation.open_app("Finder")
            
        elif "shutdown" in cmd:
            self.voice.speak("Shutting down the system. Goodbye.")
            automation.shutdown_system()
            
        elif "restart" in cmd:
            self.voice.speak("Restarting the system.")
            automation.restart_system()
            
        else:
            self.voice.speak("I'm not sure how to do that yet.")

        try:
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=["jarvis"]
            )

            # Start background monitoring
            self.monitor.start()
            
            print("Jarvis is online. Say 'Jarvis' to wake me up.")
            self.voice.speak("Jarvis is online.")
            
            # Queue for audio data
            audio_queue = queue.Queue()
            
            def wake_word_callback(indata, frames, time, status):
                if status:
                    print(status, flush=True)
                audio_queue.put(bytes(indata))

            # Open stream for Wake Word
            with sd.RawInputStream(samplerate=self.porcupine.sample_rate,
                                   blocksize=self.porcupine.frame_length,
                                   dtype='int16',
                                   channels=1,
                                   callback=wake_word_callback):
                
                while True:
                    pcm_bytes = audio_queue.get()
                    
                    # Unpack bytes to list of shorts (int16) for Porcupine
                    pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
                    
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        print("Wake word detected!")
                        logging.info("Wake word detected")
                        
                        # We are already in a context manager for the stream.
                        # We can't strictly "pause" it easily without closing or flags.
                        # But since we need to use the voice.listen() which ALSO opens a stream,
                        # we MUST close this stream or risk conflict (though sounddevice handles multiple streams ok usually).
                        # Best practice: 
                        # 1. Break inner loop to exit context manager (closes stream).
                        # 2. Call listen().
                        # 3. Re-enter loop (re-opens stream).
                        break

            # If we broke out, it means wake word detected. 
            # We need a better structure to loop forever.
            # Let's wrap the stream block in a while True.

        except KeyboardInterrupt:
            print("Stopping...")
        except Exception as e:
            print(f"Error: {e}")
            logging.error(f"Critical Error: {e}")
        finally:
            self.monitor.stop()
            if self.porcupine is not None:
                self.porcupine.delete()
                
    def run_loop(self):
        """Wrapper to handle the re-opening of the stream."""
        while True:
            try:
                self.run_wake_word_detection()
                # If we return normally, it means wake word was detected
                self.voice.speak("Yes?")
                command = self.voice.listen()
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                break

    def run_wake_word_detection(self):
        """Listens for wake word. Returns when detected."""
        audio_queue = queue.Queue()
        
        def callback(indata, frames, time, status):
             audio_queue.put(bytes(indata))
             
        with sd.RawInputStream(samplerate=self.porcupine.sample_rate,
                               blocksize=self.porcupine.frame_length,
                               dtype='int16',
                               channels=1,
                               callback=callback):
            while True:
                pcm_bytes = audio_queue.get()
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
                if self.porcupine.process(pcm) >= 0:
                    return

if __name__ == '__main__':
    app = JarvisApp()
    # Initialize porcupine and monitor before loop
    app.porcupine = pvporcupine.create(
        access_key=PORCUPINE_ACCESS_KEY,
        keywords=["jarvis"]
    )
    app.monitor.start()
    print("Jarvis is online. Say 'Jarvis' to wake me up.")
    app.voice.speak("Jarvis is online.")
    
    try:
        app.run_loop()
    except KeyboardInterrupt:
        pass
    finally:
        app.monitor.stop()
        if app.porcupine:
            app.porcupine.delete()
