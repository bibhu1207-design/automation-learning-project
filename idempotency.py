import sqlite3

connection = sqlite3.connect("events.db")
cursor = connection.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        message TEXT NOT NULL
    )
""")

connection.commit()


def save_event(event_id, message):

    try:
        cursor.execute(
            "INSERT INTO events (event_id, message) VALUES (?, ?)",
            (event_id, message)
        )

        connection.commit()

        print("Event processed and stored ✅")

    except sqlite3.IntegrityError:
        print("Duplicate event detected. Ignoring it 🚫")


# First arrival
save_event("847291", "New lead received")

# Same event arrives again
save_event("847291", "New lead received")

connection.close()