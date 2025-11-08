import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import WhisperConfig
import whisper

wmodel = whisper.load_model(name = WhisperConfig.TEST_MODEL_PATH, device=WhisperConfig.DEVICE_NAME) 

def speech_to_text(audio_path):
    result = wmodel.transcribe(audio = audio_path, language = WhisperConfig.LANGUAGE, fp16=False)
    return result

print(speech_to_text("../generated/0.wav"))
