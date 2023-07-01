import time
import schedule
from abc import ABC, abstractmethod

class Trigger(ABC):
    '''
        触发器
        用于触发任务的执行
    '''
    dir = {}
    @staticmethod
    def register(loader_name):
        def wrapper(cls):
            Trigger.dir[loader_name] = cls
            return cls
        return wrapper
    
    @staticmethod
    def getInstance(kind, params) -> "Trigger":
        return Trigger.dir[kind](params)
    
    def conversion_time(self, stamp):
        # stamp 是时间戳
        timeS = time.localtime(stamp / 1000)
        return time.strftime("%H:%M", timeS)
    
    @abstractmethod
    def monitor(self, task):
        pass

    @abstractmethod
    def stop(self):
        pass

@Trigger.register("fixed")
class FixedTrigger(Trigger):
    def __init__(self, params):
        self.job = None
        self.params = params
    
    def monitor(self, task):
        job = schedule.every().day.at(self.conversion_time(self.params.get("fixed"))).do(task.execute)
        self.job = job

    def stop(self):
        schedule.cancel_job(self.job)

@Trigger.register("interval")
class IntervalTrigger(Trigger):
    def __init__(self, params):
        self.job = None
        self.params = params
    
    def monitor(self, task):
        job = schedule.every(self.params.get("interval")).seconds.do(task.execute)
        self.job = job

    def stop(self):
        schedule.cancel_job(self.job)
