# analytics.py

import sqlite3
from backend import DB_PATH

def get_basic_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM interaction_logs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM interaction_logs WHERE success = 1")
    success = cursor.fetchone()[0]

    cursor.execute("""
        SELECT intent, COUNT(*) 
        FROM interaction_logs 
        GROUP BY intent 
        ORDER BY COUNT(*) DESC
    """)
    intents = cursor.fetchall()

    conn.close()

    return {
        "total_interactions": total,
        "successful": success,
        "success_rate": (success / total * 100) if total > 0 else 0,
        "intent_distribution": intents
    }


if __name__ == "__main__":
    stats = get_basic_stats()
    print("=== Analytics ===")
    print(f"Total interactions: {stats['total_interactions']}")
    print(f"Success rate: {stats['success_rate']:.2f}%")
    print("Intent distribution:")
    for intent, count in stats['intent_distribution']:
        print(f"  {intent}: {count}")
