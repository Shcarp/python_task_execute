import threading
import time
import schedule
from service.wrap_pb import InfoType

from task_queue import push
from info_queue import push as info_push

lock = threading.RLock()

class Synchronized():
    def __call__(self, func):
        def wrapper(self, *args, **kwargs):
            # 获取锁，确保同一时刻只有一个线程能够访问装饰的方法
            with lock:
                return func(self, *args, **kwargs)
        return wrapper

class RegisterTimeError(Exception):
    task = None
    def __init__(self, message, task):
        self.message = message
        self.task = task


class RegisterTime:
    __time_table = {}

    @Synchronized()
    def add(self, task, callback = push):
        id = task["id"]
        if (id not in self.__time_table):
            job = self.__addSchedule(task, callback)
            self.__time_table[id] = job
        else:
            oldJob = self.__time_table.pop(id)
            self.__removeSchedule(oldJob, callback)
            job = self.__addSchedule(task, callback)
            self.__time_table[id] = task
            
    @Synchronized()
    def remove(self, task):
        id = task["id"]
        if (id not in self.__time_table):
            return
        try:
            job = self.__time_table[id]
            self.__removeSchedule(job, None)
            self.__time_table.pop(id)
        except Exception as e:
            raise RegisterTimeError("remove error", e)
        

    def conversion_time(self, stamp):
        # stamp 是时间戳
        timeS = time.localtime(stamp / 1000)
        return time.strftime("%H:%M", timeS)

    def __addSchedule(self, task, callable):
        job = None
        if (task["type"] == "fixTime"):
            try:
                # 如果callback不为空，那么就要把callback传入到job中
                job = schedule.every().day.at(self.conversion_time(task["time"])).do(self.__wrap(callable , task))
                info_push(InfoType.SUCCESS, "add fixTime task: " + task["name"])
            except Exception as e:
                info_push(InfoType.ERROR, "add fixTime task error: {}".format(e))
        else:
            try:
                job = schedule.every(int(task["time"])).seconds.do(self.__wrap(callable, task))
                info_push(InfoType.SUCCESS, "add intervalTime task: " + task["name"])
            except Exception as e:
                info_push(InfoType.ERROR, "add intervalTime task error: {}".format(e))
        return job
    
    def __removeSchedule(self, job, callable):
        schedule.cancel_job(job)
        if callable is not None:
            callable()
    
    def __wrap(self, run, task):
        def inner():
            try:
                run(task)
            except Exception as e:
                print("running error: ", e)
        return inner
