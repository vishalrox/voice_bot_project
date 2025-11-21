# backend.py

import sqlite3
from pathlib import Path

DB_PATH = "bot_data.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_keyword TEXT UNIQUE,
            answer TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            balance REAL,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interaction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT,
            intent TEXT,
            response TEXT,
            success INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    seed_data()



def seed_data():
    """Insert some sample FAQ and user account data (idempotent)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    faqs = [
        ("hours", "Our customer support is available 24/7."),
        ("refund", "Refunds are processed within 5–7 business days."),
        ("delivery", "Standard delivery takes 3–5 business days."),
    ]

    for keyword, answer in faqs:
        cursor.execute(
            "INSERT OR IGNORE INTO faq (question_keyword, answer) VALUES (?, ?)",
            (keyword, answer)
        )

    users = [
        ("vishal", 2500.50, "active"),
        ("john", 120.00, "inactive"),
    ]

    for username, balance, status in users:
        cursor.execute(
            "INSERT OR IGNORE INTO user_accounts (username, balance, status) VALUES (?, ?, ?)",
            (username.lower(), balance, status)
        )

    conn.commit()
    conn.close()


def get_faq_answer(user_text: str) -> str | None:
    """Simple keyword-based FAQ answer."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT question_keyword, answer FROM faq")
    rows = cursor.fetchall()
    conn.close()

    text_lower = user_text.lower()
    for keyword, answer in rows:
        if keyword in text_lower:
            return answer
    return None


def get_account_info(username: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, balance, status FROM user_accounts WHERE username = ?",
        (username.lower(),)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "balance": row[1], "status": row[2]}
    return None


def log_interaction(user_query: str, intent: str, response: str, success: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interaction_logs (user_query, intent, response, success) VALUES (?, ?, ?, ?)",
        (user_query, intent, response, int(success))
    )
    conn.commit()
    conn.close()
