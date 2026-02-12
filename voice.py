import logging
import time
import utils

# Vosk STT + macOS TTS
# You must download a model from https://alphacephei.com/vosk/models
# and extract it to the 'models' folder.
MODEL_PATH = "models/model" 
SAMPLE_RATE = 16000

class VoiceEngine:
    def __init__(self):
        self.rec = None
        self.model = None
        self.is_speaking = False  # Track if currently speaking
        self.current_speech_process = None  # Track the speech subprocess
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
        """Text-to-speech using platform-specific command."""
        if not text:
            return
        
        print(f"Jarvis: {text}")
        try:
            self.is_speaking = True
            # Use utils.speak for platform-agnostic TTS
            self.current_speech_process = utils.speak(text)
            
            if self.current_speech_process:
                self.current_speech_process.wait()
            
            # Give some time for audio to clear before listening again
            time.sleep(0.3)
        except Exception as e:
            logging.error(f"Error speaking: {e}")
        finally:
            self.is_speaking = False
            self.current_speech_process = None
    
    def stop_speaking(self):
        """Interrupt current speech."""
        if self.current_speech_process and self.current_speech_process.poll() is None:
            try:
                self.current_speech_process.terminate()
                try:
                    self.current_speech_process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    self.current_speech_process.kill()
                    self.current_speech_process.wait()
            except Exception as e:
                logging.error(f"Error stopping speech: {e}")
            finally:
                self.current_speech_process = None
                self.is_speaking = False

    def process_audio(self, data):
        """
        Process a chunk of audio data.
        Returns (final_text, partial_text)
        - final_text: The detected command if utterance is complete.
        - partial_text: The current incomplete sentence (e.g. "open...").
        """
        if not self.rec:
            return None, None
            
        if self.rec.AcceptWaveform(data):
            # Complete utterance
            res = json.loads(self.rec.Result())
            return res.get('text', ''), ""
        else:
            # Partial utterance
            res = json.loads(self.rec.PartialResult())
            return None, res.get('partial', '')
