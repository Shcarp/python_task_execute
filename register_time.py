import threading
import time
import schedule

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

    push = None

    def __init__(self, push):
        self.push = push
        pass

    @Synchronized()
    def add(self, task):
        id = task["id"]
        if (id not in self.__time_table):
            job = self.__addSchedule(task)
            self.__time_table[id] = job
        else:
            oldJob = self.__time_table.pop(id)
            self.__removeSchedule(oldJob)
            job = self.__addSchedule(task)
            self.__time_table[id] = task
            
    @Synchronized()
    def remove(self, task):
        id = task["id"]
        if (id not in self.__time_table):
            return
        try:
            job = self.__time_table[id]
            self.__removeSchedule(job)
            self.__time_table.pop(id)
        except:
            raise RegisterTimeError("remove error", task)
        

    def conversion_time(self, stamp):
        # stamp 是时间戳
        timeS = time.localtime(stamp / 1000)
        return time.strftime("%H:%M", timeS)

    def __addSchedule(self, task):
        job = None
        if (task["type"] == "fixTime"):
            try:
                job = schedule.every().day.at(self.conversion_time(task["time"])).do(self.__wrap(task))
                print("add fixTime task: ", task["name"])
            except:
                raise RegisterTimeError("task time format error", task)
        else:
            try:
                job = schedule.every(int(task["time"])).seconds.do(self.__wrap(task))
                print("add intervalTime task: ", task["name"])
            except:
                raise RegisterTimeError("task time format error", task)
        return job
    
    def __removeSchedule(self, job):
        schedule.cancel_job(job)
    
    def __wrap(self, task):
        def inner():
            try:
                self.push(task)
            except Exception as e:
                print("running error: ", e)
        return inner
