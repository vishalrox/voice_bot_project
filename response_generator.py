from nlu import NLUResult
from backend import get_faq_answer, get_account_info

def generate_response(nlu_result: NLUResult, user_text: str) -> tuple[str, bool]:
    intent = nlu_result.intent

    if intent == "greeting":
        return "Hello! I’m your voice assistant. How can I help you today?", True

    if intent == "bot_feeling":
        return "I’m doing great, thanks for asking! How can I assist you today?", True

    if intent == "goodbye":
        return "Thank you for chatting with me. Have a great day!", True

    if intent == "refund_policy":
        ans = get_faq_answer("refund")
        return ans or "Refunds are usually processed within 5–7 business days.", True

    if intent == "delivery_info":
        ans = get_faq_answer("delivery")
        return ans or "Standard delivery usually takes 3–5 business days.", True

    if intent == "hotel_booking_help":
        msg = (
            "To book a room, please choose your dates, room type, and provide guest details. "
            "On a real system, I would connect you to the booking engine or website to complete the payment."
        )
        return msg, True

    if intent == "check_balance":
        username = nlu_result.entities.get("username")
        if not username:
            return "Sure, please tell me the username for the account.", False
        info = get_account_info(username)
        if info:
            msg = (f"Account for {info['username']} is {info['status']} "
                   f"with a balance of ₹{info['balance']:.2f}.")
            return msg, True
        return "I couldn't find that user. Please check the username.", False

    # fallback
    return "I'm not sure I understood that. Could you please rephrase?", False
