import asyncio
import queue
import threading
import time

import schedule
from runTask import worker
from service import websocket

from register_time import RegisterTime
from server import run_server

class Manage:
    _lock = threading.Lock()
    _loop = None
    _server = None
    _task_queue = None
    _regsitertime = None

    def __init__(self, port):
        self.lock = threading.Lock()
        self.loop = asyncio.new_event_loop()
        self.server = websocket.WebSocketServer(port)
        self.task_queue = queue.Queue()
        self.regsitertime =  RegisterTime(self._push_task)

    def _push_task(self, task):
        with self.lock:
            self.task_queue.put_nowait(task)
            self.loop.run_until_complete(self.server.push({
                "event": "task-size",
                "data": self.task_queue.qsize()
            }))

    def report(self, task):
      future = asyncio.run_coroutine_threadsafe(task, self.loop)
      return future.result()

    def _run_server(self):
      with self.lock:
         run_server(self.server, self.regsitertime, self.loop, self.task_queue)

    def _run_execute_task(self):
      with self.lock:
         worker(self.task_queue, self.report)

    def run(self):
      server_thread = threading.Thread(target=self._run_server)
      server_thread.start()

      task_run_thread = threading.Thread(target=self._run_execute_task)
      task_run_thread.start()

      while True:
        schedule.run_pending()
        time.sleep(1)
      
      server_thread.join()
      task_run_thread.join()
