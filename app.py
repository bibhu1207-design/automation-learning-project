from flask import Flask, request
import sqlite3
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logging.getLogger("werkzeug").setLevel(logging.WARNING)

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
# Create the database and table
def create_database():
    connection = sqlite3.connect("messages.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()

# Create the leads table
def create_leads_table():
    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()
@app.route("/message", methods=["POST"])
def receive_message():

    api_key = request.headers.get("X-API-Key")

    if api_key != API_KEY:
        return {"error": "Unauthorized"}, 401

    data = request.json

    if not data:
        return {"error": "Request must contain JSON"}, 400

    if "message" not in data:
        return {"error": "Message is required"}, 400

    message = data["message"]

    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO messages (message) VALUES (?)",
        (message,)
    )

    connection.commit()
    connection.close()

    return {"message": "Message stored successfully"}, 201

@app.route("/messages", methods=["GET"])
def get_messages():

    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM messages")

    messages = cursor.fetchall()

    connection.close()

    print(messages)

    return str(messages)

@app.route("/update/<int:message_id>", methods=["PUT"])
def update_message(message_id):

    new_message = request.json["message"]

    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE messages SET message = ? WHERE id = ?",
        (new_message, message_id)
    )

    connection.commit()
    connection.close()

    return "Message updated!"
@app.route("/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):

    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    connection.commit()
    connection.close()

    return "Message deleted!"
@app.route("/transaction-test", methods=["POST"])
def transaction_test():

    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO messages (message) VALUES (?)",
            ("Transaction test - message 1",)
        )

        cursor.execute(
            "INSERT INTO messages (message) VALUES (?)",
            ("Transaction test - message 2",)
        )

        # Deliberately cause an error
        cursor.execute("THIS IS NOT VALID SQL")

        connection.commit()

        return "Transaction committed!"

    except Exception as error:
        connection.rollback()
        return f"Transaction rolled back: {error}"

    finally:
        connection.close()

# lead route
@app.route("/lead", methods=["POST"])
def receive_lead():

    data = request.json

    if not data:
        return {"error": "JSON is required"}, 400

    if "event_id" not in data:
        return {"error": "event_id is required"}, 400

    if "name" not in data:
        return {"error": "name is required"}, 400

    if "phone" not in data:
        return {"error": "phone is required"}, 400

    event_id = data["event_id"]
    name = data["name"]
    phone = data["phone"]

    logger.info(
    "Lead received | event_id=%s | name=%s",
    event_id,
    name
)
    connection = sqlite3.connect("messages.db")
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO leads (event_id, name, phone)
            VALUES (?, ?, ?)
            """,
            (event_id, name, phone)
        )

        connection.commit()
        logger.info(
            "Lead stored successfully | event_id=%s",
            event_id
        )
    except sqlite3.IntegrityError:
        connection.rollback()

        logger.warning(
            "Duplicate lead rejected | event_id=%s",
            event_id
        )
        return {"error": "Duplicate event"}, 409
    except Exception:
        connection.rollback()

        logger.exception(
            "Lead processing failed | event_id=%s",
            event_id
        )

        return {"error": "Internal server error"}, 500

    finally:
        connection.close()

    print("New lead received!")
    print("Event ID:", event_id)
    print("Name:", name)
    print("Phone:", phone)

    return {"message": "Lead received successfully"}, 201

if __name__ == "__main__":
    print("STEP 1")
    create_database()

    print("STEP 2")
    create_leads_table()

    print("STEP 3")
    app.run(debug=True, use_reloader=False)
