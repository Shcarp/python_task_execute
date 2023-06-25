from globals import task_queue

def push(task):
    task_queue.put_nowait(task)
