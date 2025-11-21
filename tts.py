# tts.py

import pyttsx3
from time import sleep

is_speaking = False   # 🔥 shared with wake-word

engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text: str):
    global is_speaking

    if not text:
        text = "Sorry, I didn't understand that."

    print(f"🤖 Bot: {text}")

    # 🔥 lock wake word
    is_speaking = True

    engine.say(text)
    engine.runAndWait()

    sleep(0.25)  # prevent early wakeword resume
    is_speaking = False
