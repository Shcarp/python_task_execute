import asyncio
from src.globals import get_loop
from multiprocessing import JoinableQueue
from queue import Queue
from threading import Thread

class ThreadPool:
    '''
        线程池
        1、max_threads 最大线程数
        2、queue 任务队列
        3、block_queue 阻塞任务队列
        5、loop 事件循环
        6、running 是否运行中
        7、callbacks 回调函数

        通过 add_task 和 add_block_task 添加任务
        通过 wait_completion 等待任务完成, 在完成任务后会调用回调函数
    '''
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
        self.queue = Queue()
        self.block_queue = Queue()
        self.running = True

        self.loop = get_loop()

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
                output = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.loop).result()
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
                output = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.loop).result()
                callback(1, "success block: {}".format(output))
            except Exception as e:
                print(e.with_traceback())
                callback(0, e)
            finally:
                self.block_queue.task_done()

    def add_task(self, taskId, func, callback, *args, **kwargs):
        wTaskId = taskId + str(id(func))
        self.callbacks[wTaskId] = callback
        self.queue.put((func, args, kwargs, wTaskId))

    def add_block_task(self, taskId, func, callback, *args, **kwargs):
        wTaskId = taskId + str(id(func))
        self.callbacks[wTaskId] = callback
        self.block_queue.put((func, args, kwargs, wTaskId))

    def wait_completion(self):
        self.queue.join()
        self.block_queue.join()

    def stop(self):
        self.running = False
        self.block_threads.join()
        for thread in self.threads:
            thread.join()
