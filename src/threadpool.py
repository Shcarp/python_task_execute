
from multiprocessing import JoinableQueue
from threading import Thread

class ThreadPool:
    instance = None
    @staticmethod
    def getInstance(max_threads = 5):
        if ThreadPool.instance is None:
            ThreadPool.instance = ThreadPool(max_threads)
        return ThreadPool.instance

    def __init__(self, max_threads):
        self.max_threads = max_threads
        self.threads = []
        self.queue = JoinableQueue()
        self.running = True
        self._init_threads()

    def _init_threads(self):
        for _ in range(self.max_threads):
            thread = Thread(target=self._run)
            thread.start()
            self.threads.append(thread)

    def _run(self):
        while self.running:
            func, args, kwargs = self.queue.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(e)
            finally:
                self.queue.task_done()

    def add_task(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def wait_completion(self):
        self.queue.join()

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()

