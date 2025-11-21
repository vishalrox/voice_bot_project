# main.py

from backend import init_db, log_interaction
from stt import listen_for_speech
from nlu import detect_intent
from response_generator import generate_response
from tts import speak


def main():
    print("Initializing backend...")
    init_db()
    print("Voice Bot Ready.")
    print("Press Enter to speak. Type 'q' and press Enter to quit.\n")

    while True:
        cmd = input("Press Enter to speak (or 'q' to quit): ").strip().lower()
        if cmd == "q":
            speak("Goodbye! It was nice talking to you.")
            break

        user_text = listen_for_speech()
        if not user_text:
            speak("Sorry, I didn't catch that.")
            continue

        if user_text.lower() in ["exit", "quit", "bye"]:
            speak("Goodbye! See you soon.")
            break

        print(f"You: {user_text}")
        nlu_result = detect_intent(user_text)
        response, success = generate_response(nlu_result, user_text)
        speak(response)
        log_interaction(user_text, nlu_result.intent, response, success)


if __name__ == "__main__":
    main()
