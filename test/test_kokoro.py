import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kokoro import KPipeline, KModel # Genera Audio
import soundfile as sf # Salvare file audio
from pydub import AudioSegment # Unire più audio insieme

from core.config import KokoroConfig

kmodel = KModel(model=KokoroConfig.TEST_MODEL_PATH, config=KokoroConfig.TEST_CONFIG_PATH).to("cpu") #oppure "cuda"
pipeline = KPipeline(lang_code="i", model=kmodel)

def text_to_speech(text):
    generator = pipeline(text, voice=KokoroConfig.TEST_VOICE_PATH, speed=KokoroConfig.AUDIO_SPEED)

    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(f"{KokoroConfig.TEST_GENERATED_PATH}{i}.wav", audio, KokoroConfig.AUDIO_FREQ, "PCM_16")

text_to_speech("Io sono CiccioGamer89 e sono il capobranco dei miei paguri")
