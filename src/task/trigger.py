import time
from src.globals import scheduler
from abc import ABC, abstractmethod
from .serialize import Serialize

class Trigger( Serialize, ABC):
    '''
        触发器
        用于触发任务的执行
    '''
    DIR = {}
    @staticmethod
    def register(loader_name):
        def wrapper(cls):
            Trigger.DIR[loader_name] = cls
            return cls
        return wrapper
    
    @staticmethod
    def getInstance(kind, params) -> "Trigger":
        return Trigger.DIR[kind](params)
    
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
    '''
        固定时间触发器
    '''
    def __init__(self, params):
        self.job = None
        self.params = params
    
    def monitor(self, task):
        '''
            开始监控
            fixed: 固定时间，时间戳
        '''
        job = scheduler.add_job(task.execute, 'date', run_date=self.conversion_time(self.params.get("fixed")))
        self.job = job

    def stop(self):
        '''
            停止监控
        '''
        if self.job:
            self.job.remove()
            self.job = None
    
    def serialize(self):
        return {
            "kind": "fixed",
            "params": self.params
        }

@Trigger.register("interval")
class IntervalTrigger(Trigger):
    '''
        间隔时间触发器
    '''
    def __init__(self, params):
        self.job = None
        self.params = params
    
    async def monitor(self, task):
        '''
            开始监控
            interval: 间隔时间，单位秒
        '''
        try:
            job = scheduler.add_job(task.execute, 'interval', seconds=self.params.get("interval"))
            self.job = job
        except Exception as e:
            print("error", e)

    def stop(self):
        '''
            停止监控
        '''
        # 如果任务已经被删除，那么就不需要删除了
        if self.job:
            self.job.remove()
            self.job = None
    
    def serialize(self):
        return {
            "kind": "interval",
            "params": self.params
        }

# 直接运行的触发器
@Trigger.register("direct")
class DirectTrigger(Trigger):
    '''
        直接运行触发器
    '''
    def __init__(self, params):
        self.job = None
        self.params = params
    
    def monitor(self, task):
        '''
            开始监控
            interval: 间隔时间，单位秒
        '''
        task.execute()

    def stop(self):
        '''
            停止监控
        '''
        pass

    def serialize(self):
        return {
            "kind": "direct",
            "params": self.params
        }
