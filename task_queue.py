from globals import get_loop, task_queue, server

def push(task):
    task_queue.put_nowait(task)
