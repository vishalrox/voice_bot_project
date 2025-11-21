# stt.py

import sounddevice as sd
import numpy as np
import whisper

model = whisper.load_model("tiny")   # small + fast


def listen_for_speech(max_duration=8, sample_rate=16000,
                      silence_threshold=0.0005, min_voice_volume=0.001):
    print("🎙 Listening... Speak now.")

    audio_buffer = []
    silent_chunks = 0
    chunks_per_second = 10
    voice_started = False

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='float32') as stream:
        for _ in range(max_duration * chunks_per_second):
            chunk, _ = stream.read(int(sample_rate / chunks_per_second))
            volume = np.abs(chunk).mean()

            if volume > min_voice_volume:
                voice_started = True

            if voice_started:
                audio_buffer.append(chunk)

                if volume < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks > chunks_per_second * 1:
                    break

    if not audio_buffer:
        print("⚠ No speech detected.")
        return None

    audio = np.concatenate(audio_buffer).flatten()

    print("⌛ Transcribing (English forced)...")
    result = model.transcribe(
        audio,
        fp16=False,
        language="en",
        task="transcribe",
        temperature=0.0,
    )

    text = result["text"].strip()
    print(f"📝 You said: {text}")

    # Filter out garbage / non-ASCII
    if not text or any(ord(c) > 127 for c in text):
        print("⚠ Bad or non-English transcription.")
        return None

    return text
