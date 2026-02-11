import os
import queue
import sounddevice as sd
import vosk
import json
import time

# --- Configuration ---
# You must download a model from https://alphacephei.com/vosk/models
# and extract it to the 'models' folder.
MODEL_PATH = "models/model" 
SAMPLE_RATE = 16000

class VoiceEngine:
    def __init__(self):
        self.q = queue.Queue()
        self.rec = None
        self.setup_vosk()

    def setup_vosk(self):
        """Initialize Vosk recognizer."""
        if not os.path.exists(MODEL_PATH):
            print(f"Warning: Vosk model not found at {MODEL_PATH}. Speech recognition will not work until you download it.")
            return
        
        try:
            model = vosk.Model(MODEL_PATH)
            self.rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
        except Exception as e:
            print(f"Failed to load Vosk model: {e}")

    def speak(self, text):
        """
        Speak text using macOS native 'say' command (High Quality, Offline).
        This blocks until speaking is done to avoid listening to itself.
        """
        if not text:
            return
        print(f"Jarvis: {text}")
        # Escape quotes to prevent shell injection/errors
        safe_text = text.replace('"', '\\"')
        os.system(f'say "{safe_text}"')

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice input stream."""
        if status:
            print(status, flush=True)
        self.q.put(bytes(indata))

    def listen(self, timeout=5):
        """
        Listen for a command for a specific duration or until silence.
        Returns the recognized text.
        """
        if not self.rec:
            return ""

        print("Listening...")
        # Play a subtle listening sound (optional, skipping for now)
        
        start_time = time.time()
        result_text = ""

        try:
            with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, device=None,
                                   dtype='int16', channels=1, callback=self._audio_callback):
                
                while True:
                    # Check timeout
                    if time.time() - start_time > timeout:
                        break
                    
                    data = self.q.get()
                    if self.rec.AcceptWaveform(data):
                        res = json.loads(self.rec.Result())
                        if res['text']:
                            result_text = res['text']
                            break
                    else:
                        # Partial result (optional to look at)
                        pass
                        
        except Exception as e:
            print(f"Error during listening: {e}")
            
        print(f"Heard: {result_text}")
        return result_text
