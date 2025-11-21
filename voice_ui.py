# voice_ui.py

import threading
import tkinter as tk

from backend import init_db, log_interaction
from stt import listen_for_speech
from nlu import detect_intent
from response_generator import generate_response
from tts import speak

# wake word is optional
try:
    from wakeword_porcupine import porcupine_wake_word
    WAKEWORD_AVAILABLE = True
except Exception as e:
    print("Wake word disabled:", e)
    WAKEWORD_AVAILABLE = False


class VoiceBotUI:

    def __init__(self, root):
        self.root = root
        self.root.title("AI Voice Bot")
        self.root.geometry("480x620")
        self.root.configure(bg="#FFFFFF")

        tk.Label(root, text="AI Voice Assistant",
                 font=("Helvetica", 20, "bold"),
                 bg="#FFFFFF", fg="#0078FF").pack(pady=10)

        self.chat_box = tk.Text(root, font=("Helvetica", 13),
                                bg="#F1F3F4", fg="#333333",
                                width=55, height=26, wrap="word", bd=0)
        self.chat_box.pack(padx=10, pady=10)

        self.mic_btn = tk.Button(root, text="🎤 Speak",
                                 command=self.manual_listen,
                                 font=("Helvetica", 15),
                                 bg="#0078FF", fg="white", bd=0,
                                 padx=20, pady=8)
        self.mic_btn.pack(pady=8)

        self.status = tk.Label(root, text="", font=("Helvetica", 10),
                               bg="#FFFFFF", fg="#555555")
        self.status.pack()

        init_db()

        if WAKEWORD_AVAILABLE:
            self.status.config(text="Say 'Jarvis' to wake the bot or press Speak.")
            threading.Thread(target=self.wakeword_loop, daemon=True).start()
        else:
            self.status.config(text="Wake word not available. Use 'Speak' button.")

    def wakeword_loop(self):
        while True:
            porcupine_wake_word()
            self.run_interaction()

    def manual_listen(self):
        threading.Thread(target=self.run_interaction, daemon=True).start()

    def run_interaction(self):
        self.status.config(text="Listening...")
        user_text = listen_for_speech()
        self.status.config(text="")

        if not user_text:
            speak("Sorry, I didn't catch that.")
            return

        self.chat_box.insert(tk.END, f"\nYou: {user_text}\n")
        self.chat_box.see(tk.END)

        nlu_result = detect_intent(user_text)
        response, success = generate_response(nlu_result, user_text)

        self.chat_box.insert(tk.END, f"Bot: {response}\n")
        self.chat_box.see(tk.END)

        speak(response)
        log_interaction(user_text, nlu_result.intent, response, success)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceBotUI(root)
    root.mainloop()
