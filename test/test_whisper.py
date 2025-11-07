import whisper

from core.config import WhisperConfig

wmodel = whisper.load_model(name = WhisperConfig.TEST_MODEL_PATH, device=WhisperConfig.DEVICE_NAME) 

def speech_to_text(audio_path):
    result = wmodel.transcribe(audio = audio_path, language = WhisperConfig.LANGUAGE, fp16=False)
    return result

print(speech_to_text("C:/Users/simone.siega/aicompanion/generated/0.wav"))

# pip install openai-whisper
# winget install ffmpeg 
