import sys
import threading
import uuid
from .serialize import Serialize
from .threadpool import ThreadPool
from .execute import Execute
from .trigger import Trigger

class TaskConfig:
    def __init__(self, name, run_count, trigger_type, trigger_info, execute_type, execute_info, block=False):
        self.name = name
        self.run_count = run_count
        self.trigger_type = trigger_type
        self.trigger_info = trigger_info
        self.execute_type = execute_type
        self.execute_info = execute_info
        self.block = block


class Task(Serialize):
    '''
        任务类
        1、trigger  触发器 用来触发任务脚本的执行, 根据trigger_type来选择不同的触发器
        2、executer 执行器 用来执行任务脚本, 根据execute_type来选择不同的执行器
        3、block 是否阻塞, 如果阻塞, 则任务脚本执行完毕后, 才会执行下一个任务脚本, 如果不是阻塞, 会立即执行下一个任务脚本
        4、run_status 1: 运行中 2: 运行完毕 3: 运行失败
        5、run_count 运行次数、当运行次数为0时, 任务脚本不会再执行、且将状态设置为运行完毕
    '''
    def __init__(self, config: TaskConfig):
        self.exe_status = 0
        self.lock = threading.Lock()
        self.task_manage = None
        self.run_status = 0
        self.id = str(uuid.uuid4())
        self.name = config.name
        self.block = config.block
        self.run_count = config.run_count
        self.trigger = Trigger.getInstance(kind=config.trigger_type, params=config.trigger_info)
        self.executer = Execute.getInstance(kind=config.execute_type, config=config.execute_info)

    async def init(self):
        await self.executer.init()

    async def start(self):
        '''
            开始执行任务
        '''
        await self.trigger.monitor(self)
        # 设置状态为运行中
        self.run_status = 1

    def cancel(self):
        '''
            取消任务
        '''
        # 设置状态为停止
        self.run_status = 0
        self._stop()

    def _stop(self):
        '''
            停止任务
        '''
        self.trigger.stop()
        self.executer.stop()
    
    def execute(self):
        '''
            执行任务
            1. 判断任务是否已经停止, 如果run_status为0 或者 run_count <= 0 则停止任务
            2. 通过线程池执行任务
        '''
        self.lock.acquire()
        if self.run_status != 1 or self.run_count <= 0:
            self.lock.release()
            self.trigger.stop()
            return
        self.run_count = self.run_count - 1
        self.lock.release()

        if self.run_count <= 0:
            self.trigger.stop()

        def callback(status, message):
            if status == 0:
                self.run_status = 3
                print("execute failed " + self.name, self.run_count, message)
            else:
                print("execute success " + self.name, self.run_count, message)
                if self.run_count <= 0:
                    self.run_status = 2

        # 执行，根据是否阻塞来决定通过什么方式执行
        if not self.block:
            ThreadPool.getInstance().add_task(taskId=self.id, func=self.executer.execute, callback=callback)
        else:
            ThreadPool.getInstance().add_block_task(taskId=self.id, func=self.executer.execute, callback=callback)

    # 序列化
    def serialize(self):
        '''
            序列化
        '''
        return {
            "id": self.id,
            "name": self.name,
            "run_status": self.run_status,
            "run_count": self.run_count,
            "trigger": self.trigger.serialize(),
            "executer": self.executer.serialize(),
            "block": self.block
        }

