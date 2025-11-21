# nlu.py

import re
from dataclasses import dataclass


@dataclass
class NLUResult:
    intent: str
    entities: dict


def extract_username(text: str) -> str | None:
    patterns = [
        r"my name is ([a-zA-Z0-9_]+)",
        r"for user ([a-zA-Z0-9_]+)",
        r"for account ([a-zA-Z0-9_]+)",
    ]
    t = text.lower()
    for pattern in patterns:
        m = re.search(pattern, t)
        if m:
            return m.group(1)
    return None


def detect_intent(text: str) -> NLUResult:
    t = text.lower()

    # Greetings / small talk
    if any(w in t for w in ["hi", "hello", "hey", "good morning", "good evening"]):
        return NLUResult(intent="greeting", entities={})

    if "how are you" in t:
        return NLUResult(intent="bot_feeling", entities={})

    # Goodbye
    if any(w in t for w in ["bye", "goodbye", "see you"]):
        return NLUResult(intent="goodbye", entities={})

    # Policies / support
    if any(w in t for w in ["refund", "return"]):
        return NLUResult(intent="refund_policy", entities={})

    if any(w in t for w in ["delivery", "shipping", "order status"]):
        return NLUResult(intent="delivery_info", entities={})

    # Hotel booking
    if any(w in t for w in ["book a room", "room booking", "hotel booking", "reserve a room"]):
        return NLUResult(intent="hotel_booking_help", entities={})

    # Account / balance
    if any(w in t for w in ["balance", "account", "my money"]):
        username = extract_username(t)
        return NLUResult(intent="check_balance", entities={"username": username})

    # fallback
    return NLUResult(intent="fallback", entities={})
