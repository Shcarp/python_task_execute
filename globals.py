import asyncio
import queue

from service import websocket

loop = None

def get_loop():
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
    return loop

server = websocket.WebSocketServer()
task_queue = queue.Queue()
