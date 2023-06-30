
from abc import ABC, abstractmethod
from task.base import Task

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
    
    @abstractmethod
    def monitor(self, task: Task):
        pass

    @abstractmethod
    def stop():
        pass

@Trigger.register("fixed")
class FixedTrigger(Trigger):
    def __init__(self, params):
        self.params = params
    
    def monitor(self, task: Task):
        pass

    def stop(self, task: Task):
        pass

@Trigger.register("interval")
class IntervalTrigger(Trigger):
    def __init__(self, params):
        self.params = params
    
    def monitor(self, task: Task):
        pass

    def stop(self, task: Task):
        pass
