
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
        self.callbacks = {}
        self.max_threads = max_threads
        self.threads = []
        self.block_threads = None
        self.queue = JoinableQueue()
        self.block_queue = JoinableQueue()
        self.running = True
        self._init_threads()

    def _init_threads(self):
        for _ in range(self.max_threads):
            thread = Thread(target=self._run)
            thread.start()
            self.threads.append(thread)
        
        self.block_threads = Thread(target=self._block_run)
        self.block_threads.start()
       

    def _run(self):
        while self.running:
            func, args, kwargs, id = self.queue.get()
            callback = self.callbacks[id]
            try:
                output = func(*args, **kwargs)
                callback(1, "success no block: {}".format(output))
            except Exception as e:
                print(e)
                callback(0, e)
            finally:
                self.queue.task_done()

    def _block_run(self):
        '''
            同时只能有一个执行
        '''
        while self.running:
            func, args, kwargs, id = self.block_queue.get()
            callback = self.callbacks[id]
            try:
                output = func(*args, **kwargs)
                callback(1, "success block: {}".format(output))
            except Exception as e:
                print(e)
                callback(0, e)
            finally:
                self.block_queue.task_done()

    def add_task(self, taskId, func, callback, *args, **kwargs):
        self.callbacks[taskId] = callback
        self.queue.put((func, args, kwargs, taskId))

    def add_block_task(self, taskId, func, callback, *args, **kwargs):
        self.callbacks[taskId] = callback
        self.block_queue.put((func, args, kwargs, taskId))

    def wait_completion(self):
        self.queue.join()
        self.block_queue.join()

    def stop(self):
        self.running = False
        self.block_threads.join()
        for thread in self.threads:
            thread.join()
        

