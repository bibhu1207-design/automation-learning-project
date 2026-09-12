import requests
import sqlite3
import time
data = None
# ─────────────────────────
# API REQUEST + RETRY
# ─────────────────────────

for attempt in range(3):

    try:
        print(f"Attempt {attempt + 1}...")

        response = requests.get(
            "https://jsonplaceholder.typicode.com/users/999999",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()

        print("API request successful!")

        break

    except requests.exceptions.Timeout:
        print("Request timed out.")

    except requests.exceptions.HTTPError as error:
        status = error.response.status_code

        print(f"HTTP error: {status}")

        if status >= 500:
            print("Server problem. We can retry. ")
            
        else:
            print("Client-side error. Retrying is probably pointless.")
            break
    except requests.exceptions.RequestException as error:
        print("Network error:", error)

if data is None:
    print("Could not get valid data. Stopping.")
    exit()
# ─────────────────────────
# EXTRACT USEFUL INFORMATION
# ─────────────────────────

name = data["name"]
email = data["email"]

print("Name:", name)
print("Email:", email)


# ─────────────────────────
# STORE IN DATABASE
# ─────────────────────────

connection = sqlite3.connect("api_data.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")

cursor.execute(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    (name, email)
)

connection.commit()
connection.close()

print("User stored in database!")