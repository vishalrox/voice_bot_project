# wakeword_porcupine.py

from dotenv import load_dotenv
load_dotenv()

import os
import struct
import pvporcupine
import pyaudio
from tts import is_speaking   # 🔥 NEW: import speaking lock


def porcupine_wake_word():
    """
    Listens continuously for the hotword 'Jarvis'.
    Pauses automatically while the bot is speaking (prevents cutting off audio).
    Requires PORCUPINE_ACCESS_KEY in .env
    """

    access_key = os.getenv("PORCUPINE_ACCESS_KEY")
    if not access_key:
        raise RuntimeError(
            "PORCUPINE_ACCESS_KEY not set. Please set it in your environment "
            "to use wake word detection."
        )

    porcupine = pvporcupine.create(access_key=access_key, keywords=["jarvis"])

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("👂 Waiting for wake word: 'Jarvis'...")

    try:
        while True:

            # 🔥 Don't listen for wake word while TTS is speaking
            if is_speaking:
                continue

            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("🚀 Wake word detected!")
                return True

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
