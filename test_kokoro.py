from kokoro import KPipeline, KModel # Genera Audio
import soundfile as sf # Salvare file audio
from pydub import AudioSegment # Unire più audio insieme

kmodel = KModel(model="models/kokoro-v1_0.pth", config="models/config.json").to("cpu") #oppure "cuda"
pipeline = KPipeline(lang_code="i", model=kmodel)


def text_to_speech(text):
    generator = pipeline(text, voice="models/voices/af_jessica.pt", speed=0.9)


    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(f"generated/{i}.wav", audio, 24000, "PCM_16")


text_to_speech("Ciao! Questa è una prova della voce sintetica generata da Kokoro.")