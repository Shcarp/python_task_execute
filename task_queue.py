from globals import task_queue, server, loop

def push(task):
    task_queue.put_nowait(task)
    loop.run_until_complete(server.push({
        "event": "task-size",
        "data": task_queue.qsize()
    }))