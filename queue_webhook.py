from flask import Flask, request
from queue import Queue
import threading
import time

app = Flask(__name__)

jobs = Queue()


def worker():
    while True:
        job = jobs.get()

        print("Worker processing:", job)

        # Pretend this is slow work
        time.sleep(3)

        print("Finished:", job)

        jobs.task_done()


worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()


@app.route("/lead", methods=["POST"])
def receive_lead():

    data = request.json

    jobs.put(data)

    print("Lead added to queue:", data)

    return {"message": "Lead accepted"}, 202


if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )