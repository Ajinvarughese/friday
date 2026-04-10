import riva.client
import sounddevice as sd
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("NVIDIA_TTS_API_KEY")

def stream_tts(text, emotion="default"):
    auth = riva.client.Auth(
        uri="grpc.nvcf.nvidia.com:443",
        use_ssl=True,
        metadata_args=[
            ("authorization", f"Bearer {API_KEY}"),
            ("function-id", "877104f7-e885-42b9-8de8-f6e4c6303969"),
            ("emotion", emotion),
            ("language", "en-US")
        ]
    )

    tts_service = riva.client.SpeechSynthesisService(auth)

    responses = tts_service.synthesize_online(
        text=text,
        voice_name="Magpie-Multilingual.EN-US.Aria",
        language_code="en-US",
        sample_rate_hz=22050
    )

    # open continuous audio stream
    stream = sd.OutputStream(
        samplerate=22050,
        channels=1,
        dtype='int16'
    )
    stream.start()

    for response in responses:
        if response.audio:
            audio = np.frombuffer(response.audio, dtype=np.int16)
            stream.write(audio)

    stream.stop()
    stream.close()
