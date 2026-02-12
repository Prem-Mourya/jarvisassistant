try:
    import pvporcupine
except Exception as e:
    # Catching broad Exception because pvporcupine raises NotImplementedError or others during init on some ARM chips
    pvporcupine = None
    print(f"Warning: pvporcupine failed to load ({e}). Wake word detection will be disabled.")
import struct
import queue
import sounddevice as sd
import time
import logging
import threading
import sys
import subprocess
import gc  # Added for memory management

# Local imports
from voice import VoiceEngine
from monitor import SystemMonitor
import automation
import utils
from knowledge import KnowledgeBase

# Constants
WAKE_WORD = "jarvis"
LISTENING_TIMEOUT = 5  # Seconds to wait for command
CONVERSATION_TIMEOUT = 15  # Seconds to stay active in conversation mode

# --- Configuration ---
# Get your FREE AccessKey from https://console.picovoice.ai/
PORCUPINE_ACCESS_KEY = "lJNt7xoOq7FnbPEcxej/ErPNuh/8+5VUduG3a3+sbeR5DrqCHjj/hg==" 

# Setup Logging
logging.basicConfig(filename='jarvis.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class JarvisApp:
    def __init__(self):
        self.voice = VoiceEngine()
        self.monitor = SystemMonitor(self.monitor_callback)
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.knowledge = KnowledgeBase()
        self.running = False  # Flag to control the main loop
        # Force garbage collection after initialization
        gc.collect()

    def init_porcupine(self):
        """Initialize Porcupine if available."""
        if not pvporcupine:
            return
            
        try:
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=["jarvis"]
            )
        except Exception as e:
            print(f"Failed to initialize Porcupine: {e}")
            self.porcupine = None

    def stop(self):
        """Stop the application loop."""
        self.running = False
        if self.audio_stream:
            self.audio_stream.stop()
            
    # ... (methods execute_with_retry, monitor_callback, normalize_command, process_command remain unchanged)

    def run_loop(self):
        """Main loop managing a SINGLE audio stream for both Wake Word and Voice Command."""
        # Use a bounded queue to prevent memory leaks during slow processing
        audio_queue = queue.Queue(maxsize=100)
        self.running = True
        
        def callback(indata, frames, time, status):
             if status:
                 print(status, flush=True)
             try:
                 if self.running:
                    audio_queue.put_nowait(bytes(indata))
             except queue.Full:
                 # If queue is full, we drop the frame (better than crashing or unbounded memory)
                 pass
             
        # State constants
        STATE_WAKE = "WAKE"
        STATE_LISTEN = "LISTEN"
        current_state = STATE_WAKE
        in_conversation = False  # Track if we're in continuous conversation mode
        
        listen_start_time = 0
        last_speech_time = 0  # Track when we last heard speech
        last_partial = ""  # Track last partial to avoid spam
             
        try:
            with sd.RawInputStream(samplerate=self.porcupine.sample_rate,
                                   blocksize=self.porcupine.frame_length,
                                   dtype='int16',
                                   channels=1,
                                   callback=callback):
                
                self.audio_stream = sd.get_stream()
                print("Audio stream started. Waiting for 'Jarvis'...")
                
                while self.running:
                    try:
                        # Get audio chunk with timeout to allow checking self.running
                        try:
                            pcm_bytes = audio_queue.get(timeout=0.1)
                        except queue.Empty:
                            continue
                        
                        # Skip processing if Jarvis is speaking (avoid feedback loop)
                        if self.voice.is_speaking:
                            continue
                        
                        if current_state == STATE_WAKE:
                            # Process for Wake Word
                            if self.porcupine:
                                # Porcupine requires list of shorts
                                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
                                keyword_index = self.porcupine.process(pcm)
                                
                                if keyword_index >= 0:
                                    print("Wake word detected!")
                                    logging.info("Wake word detected")
                                    # Play notification sound
                                    if utils.PLATFORM == "mac":
                                        utils.play_sound("/System/Library/Sounds/Tink.aiff")
                                    
                                    # Clear queue
                                    with audio_queue.mutex:
                                        audio_queue.queue.clear()
                                        
                                    current_state = STATE_LISTEN
                                    in_conversation = True
                                    listen_start_time = time.time()
                                    last_speech_time = time.time()
                                    print("Listening for command...")
                            else:
                                # No wake word engine, default to always listening / conversation mode
                                # But we need to throttle or it might be chaotic.
                                # Let's just switch to LISTEN state immediately.
                                current_state = STATE_LISTEN
                                in_conversation = True
                                last_speech_time = time.time()
                                print("No wake word engine. Listening for command...")

                        elif current_state == STATE_LISTEN:
                            # Determine timeout based on conversation mode
                            timeout = CONVERSATION_TIMEOUT if in_conversation else LISTENING_TIMEOUT
                            time_elapsed = time.time() - last_speech_time
                            
                            # Check timeout
                            if time_elapsed > timeout:
                                if in_conversation:
                                    print("Conversation timeout. Going back to sleep.")
                                    self.voice.speak("Going to sleep.")
                                else:
                                    print("Command timeout. Going back to sleep.")
                                current_state = STATE_WAKE
                                in_conversation = False
                                continue

                            # Process for Voice Command (Vosk)
                            final_text, partial_text = self.voice.process_audio(pcm_bytes)
                            
                            if partial_text and partial_text != last_partial:
                                # Reset timeout on any speech detected
                                last_speech_time = time.time()
                                last_partial = partial_text
                                print(f"Partial: {partial_text}")
                            
                            if final_text:
                                print(f"Heard: {final_text}")
                                last_partial = ""  # Reset for next command
                                result = self.process_command(final_text)
                                
                                # Clear queue after command to avoid processing TTS output
                                with audio_queue.mutex:
                                    audio_queue.queue.clear()
                                
                                # Check if command requested exit from conversation
                                if result == "EXIT_CONVERSATION":
                                    current_state = STATE_WAKE
                                    in_conversation = False
                                    print("Waiting for 'Jarvis'...")
                                else:
                                    # Stay in listen mode (conversation mode)
                                    last_speech_time = time.time()
                                    print("Ready for next command...")

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        logging.error(f"Loop error: {e}")
                        continue
                        
        except Exception as e:
            print(f"Stream Error: {e}")
            logging.error(f"Stream Critical Error: {e}")
        """Execute an action with specific retry logic and voice feedback."""
        for attempt in range(retries):
            try:
                if action_func():
                    self.voice.speak(success_msg)
                    return True
                else:
                    logging.warning(f"Action failed, attempt {attempt+1}/{retries}")
            except Exception as e:
                 logging.error(f"Action error: {e}")
            
            if attempt < retries - 1:
                self.voice.speak("Retrying...")
                time.sleep(1)
        
        self.voice.speak(fail_msg)
        return False

    def monitor_callback(self, category, message):
        """
        Callback for system monitoring alerts.
        Speak the alert message naturally.
        """
        print(f"[ALERT - {category}] {message}")
        # Only speak if not currently speaking to avoid interruption
        if not self.voice.is_speaking:
            self.voice.speak(message)

    def normalize_command(self, text):
        """Normalize voice command text."""
        text = text.lower().strip()
        
        # Remove all instances of common filler words
        filler_words = ["the", "a", "an", "um", "uh", "okay", "that", "is", "are"]
        words = text.split()
        
        # Filter out filler words entirely
        filtered_words = [w for w in words if w not in filler_words]
        text = " ".join(filtered_words)
        
        # Fix common domain speech patterns
        text = text.replace(" dot com", ".com").replace(" dot net", ".net").replace(" dot org", ".org")
        text = text.replace(" dot ", ".")
        
        # Heuristics for common misheard commands
        text = text.replace("open you tube", "open youtube")
        text = text.replace("calculatorg", "calculator").replace("calculatorns", "calculator")
        text = text.replace("close", "close").replace("glows", "close").replace("globe", "close")
        text = text.replace("search for", "search").replace("google for", "google")
        
        # Autostart variations
        if "enable" in text and ("start" in text or "stat" in text):
            text = "enable autostart"
        if "run" in text and ("start" in text or "up" in text):
            text = "enable autostart"
            
        return text.strip()

    def process_command(self, command):
        """Process the text command received from Voice Engine."""
        cmd = self.normalize_command(command)
        logging.info(f"Command received: {cmd}")
        
        # Check for exit conversation commands first
        if any(word in cmd for word in ["bye", "stop", "sleep", "that's all", "thanks", "thank you"]):
            # If speaking, stop the speech
            if self.voice.is_speaking:
                self.voice.stop_speaking()
                self.voice.speak("Stopping.")
                return  # Don't exit conversation, just stop speech
            else:
                self.voice.speak("Going to sleep. Say Jarvis to wake me up.")
                return "EXIT_CONVERSATION"
        
        result_status = None
        
        if "time" in cmd:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            self.voice.speak(f"It is currently {now}")

        elif "enable autostart" in cmd or "run on startup" in cmd:
            self.voice.speak("Enabling Jarvis to run on startup.")
            if automation.setup_autostart():
                 self.voice.speak("Autostart enabled successfully.")
            else:
                 self.voice.speak("Failed to enable autostart.")
            
        elif "status" in cmd or "system" in cmd:
            summary = self.monitor.get_status_summary()
            self.voice.speak(summary)
            
        elif "close" in cmd:
            # Extract app name: "close calculator" -> "calculator"
            app_name = cmd.replace("close", "").strip()
            if app_name:
                self.voice.speak(f"Closing {app_name}")
                self.execute_with_retry(lambda: automation.close_app(app_name))
            else:
                self.voice.speak("Which app should I close?")

        elif "memory" in cmd and ("taking" in cmd or "digging" in cmd or "more" in cmd or "most" in cmd):
            # "what is taking more memory"
            self.voice.speak("Checking process memory usage...")
            report = self.monitor.get_top_memory_process()
            self.voice.speak(report)

        elif "search" in cmd or "google" in cmd:
            # "search for python tutorials"
            query = cmd.replace("search", "").replace("google", "").replace("for", "").strip()
            if query:
                self.voice.speak(f"Searching Google for {query}")
                url = f"https://www.google.com/search?q={query}"
                utils.open_url(url)
            else:
                 self.voice.speak("What should I search for?")

        elif "open" in cmd and (".com" in cmd or ".net" in cmd or ".org" in cmd or "website" in cmd):
             # "open youtube.com"
            domain = cmd.replace("open", "").replace("website", "").strip()
            # Cleanup any trailing/leading dots or spaces
            domain = domain.strip().strip(".")
            
            if domain:
                self.voice.speak(f"Opening {domain}")
                if not domain.startswith("http"):
                    domain = "https://" + domain
                utils.open_url(domain)

        elif "weather" in cmd:
             self.voice.speak("Checking weather on Google")
             utils.open_url("https://www.google.com/search?q=weather")

        elif "tell me" in cmd or "who is" in cmd or "what is" in cmd or "ask" in cmd:
            # Voice Q&A - check if suitable for Wikipedia or needs web search
            answer = self.knowledge.get_answer(cmd)
            if answer:
                # Check if answer indicates we should search Google instead
                if "search Google instead" in answer or "latest" in answer.lower():
                    self.voice.speak(answer)
                    # Open Google search
                    import urllib.parse
                    import webbrowser
                    query = cmd.replace("tell me", "").replace("who is", "").replace("what is", "").replace("ask", "").strip()
                    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                    utils.open_url(search_url)
                else:
                    logging.info(f"Answer found: {answer}")
                    self.voice.speak(answer)
            else:
                self.voice.speak("I couldn't find an answer.")

        elif "calculator" in cmd:
            self.voice.speak("Opening Calculator")
            self.execute_with_retry(lambda: automation.open_app("Calculator"))
            
        elif "notes" in cmd:
            self.voice.speak("Opening Notes")
            self.execute_with_retry(lambda: automation.open_app("Notes"))
            
        # Generic "open X" command for any application
        elif "open" in cmd:
            app_name = cmd.replace("open", "").strip()
            if app_name:
                # Capitalize the app name properly
                app_name = app_name.title()
                self.voice.speak(f"Opening {app_name}")
                self.execute_with_retry(lambda: automation.open_app(app_name))
            else:
                self.voice.speak("What should I open?")
            
        elif "safari" in cmd:
            self.voice.speak("Opening Safari")
            self.execute_with_retry(lambda: automation.open_app("Safari"))
            
        elif "activity monitor" in cmd:
            self.voice.speak("Opening Activity Monitor")
            self.execute_with_retry(lambda: automation.open_app("Activity Monitor"))
            
        elif "finder" in cmd:
            self.voice.speak("Opening Finder")
            self.execute_with_retry(lambda: automation.open_app("Finder"))
            
        elif "shutdown" in cmd:
            self.voice.speak("Shutting down the system. Goodbye.")
            automation.shutdown_system()
            
        elif "restart" in cmd:
            self.voice.speak("Restarting the system.")
            automation.restart_system()
            
        else:
            self.voice.speak("I'm not sure how to do that yet.")

        # Trigger GC after processing a command
        gc.collect()
        return result_status


    def run_loop(self):
        """Main loop managing a SINGLE audio stream for both Wake Word and Voice Command."""
        # Use a bounded queue to prevent memory leaks during slow processing
        audio_queue = queue.Queue(maxsize=100)
        
        def callback(indata, frames, time, status):
             if status:
                 print(status, flush=True)
             try:
                 audio_queue.put_nowait(bytes(indata))
             except queue.Full:
                 # If queue is full, we drop the frame (better than crashing or unbounded memory)
                 pass
             
        # State constants
        STATE_WAKE = "WAKE"
        STATE_LISTEN = "LISTEN"
        current_state = STATE_WAKE
        in_conversation = False  # Track if we're in continuous conversation mode
        
        listen_start_time = 0
        last_speech_time = 0  # Track when we last heard speech
        last_partial = ""  # Track last partial to avoid spam
             
        try:
            with sd.RawInputStream(samplerate=self.porcupine.sample_rate,
                                   blocksize=self.porcupine.frame_length,
                                   dtype='int16',
                                   channels=1,
                                   callback=callback):
                
                print("Audio stream started. Waiting for 'Jarvis'...")
                
                while True:
                    try:
                        # Get audio chunk
                        pcm_bytes = audio_queue.get()
                        
                        # Skip processing if Jarvis is speaking (avoid feedback loop)
                        if self.voice.is_speaking:
                            continue
                        
                        if current_state == STATE_WAKE:
                            # Process for Wake Word
                            # Porcupine requires list of shorts
                            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm_bytes)
                            keyword_index = self.porcupine.process(pcm)
                            
                            if keyword_index >= 0:
                                print("Wake word detected!")
                                logging.info("Wake word detected")
                                # Play notification sound to indicate listening
                                subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"], check=False)
                                
                                # Clear queue to avoid processing own voice
                                with audio_queue.mutex:
                                    audio_queue.queue.clear()
                                    
                                current_state = STATE_LISTEN
                                in_conversation = True
                                listen_start_time = time.time()
                                last_speech_time = time.time()
                                print("Listening for command...")

                        elif current_state == STATE_LISTEN:
                            # Determine timeout based on conversation mode
                            timeout = CONVERSATION_TIMEOUT if in_conversation else LISTENING_TIMEOUT
                            time_elapsed = time.time() - last_speech_time
                            
                            # Check timeout
                            if time_elapsed > timeout:
                                if in_conversation:
                                    print("Conversation timeout. Going back to sleep.")
                                    self.voice.speak("Going to sleep.")
                                else:
                                    print("Command timeout. Going back to sleep.")
                                current_state = STATE_WAKE
                                in_conversation = False
                                continue

                            # Process for Voice Command (Vosk)
                            final_text, partial_text = self.voice.process_audio(pcm_bytes)
                            
                            if partial_text and partial_text != last_partial:
                                # Reset timeout on any speech detected
                                last_speech_time = time.time()
                                last_partial = partial_text
                                print(f"Partial: {partial_text}")
                            
                            if final_text:
                                print(f"Heard: {final_text}")
                                last_partial = ""  # Reset for next command
                                result = self.process_command(final_text)
                                
                                # Clear queue after command to avoid processing TTS output
                                with audio_queue.mutex:
                                    audio_queue.queue.clear()
                                
                                # Check if command requested exit from conversation
                                if result == "EXIT_CONVERSATION":
                                    current_state = STATE_WAKE
                                    in_conversation = False
                                    print("Waiting for 'Jarvis'...")
                                else:
                                    # Stay in listen mode (conversation mode)
                                    last_speech_time = time.time()
                                    print("Ready for next command...")

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        logging.error(f"Loop error: {e}")
                        continue
                        
        except Exception as e:
            print(f"Stream Error: {e}")
            logging.error(f"Stream Critical Error: {e}")



if __name__ == '__main__':
    app = JarvisApp()
    # Initialize porcupine and monitor before loop
    app.init_porcupine()

    app.monitor.start()
    print("Jarvis is online. Say 'Jarvis' to wake me up.")
    app.voice.speak("Jarvis is online. sir!")
    
    try:
        app.run_loop()
    except KeyboardInterrupt:
        pass
    finally:
        app.monitor.stop()
        if app.porcupine:
            app.porcupine.delete()
