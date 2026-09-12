from queue import Queue

jobs = Queue()

# Incoming work
jobs.put("Lead 1")
jobs.put("Lead 2")
jobs.put("Lead 3")

print("Jobs waiting:", jobs.qsize())

# Worker
while not jobs.empty():
    job = jobs.get()

    print("Processing:", job)

    jobs.task_done()

print("All jobs processed!")