import uuid
from task.execute import Execute
from task.trigger import Trigger

class TaskConfig:
    # name
    name: str = None
    # 运行次数
    run_count: int = 0
    # 运行状态
    run_status: int = 0
    # 触发
    trigger_type: str = None # time, cron, ...
    # trigger_info
    trigger_info: dict = None # { time: 3000 }
    # type
    execute_type: str = None # python, shell, java, go, ...
    # info
    execute_info: dict = None  # { "key": "xxx", "location": "xxx", "path": "xxx", "params": "xxx", "mode": "xxx" }
    # block
    block: bool = False

    def __init__(self, name, run_count, run_status, trigger_type, trigger_info, execute_type, execute_info, block=False):
        self.name = name
        self.run_count = run_count
        self.run_status = run_status
        self.trigger_type = trigger_type
        self.trigger_info = trigger_info
        self.execute_type = execute_type
        self.execute_info = execute_info
        self.block = block

class Task:
    def __init__(self, config: TaskConfig):
        self.id = str(uuid.uuid4())
        self.name = config.name
        self.run_count = config.run_count
        self.run_status = config.run_status
        self.trigger = Trigger.getInstance(kind=config.trigger_type, config=config.trigger_info)
        self.execute = Execute.getInstance(kind=config.execute_type, config=config.execute_info)

    # 添加task_manage的引用
    def add_task_manage(self, task_manage):
        self.task_manage = task_manage

    def start(self):
        self.trigger.monitor(self)
        # 设置状态为运行中
        self.run_status = 1

    def stop(self):
        self.trigger.stop(self)
        # 设置状态为停止
        self.run_status = 0
    
    def execute(self):
        # run_count 减少
        self.run_count -= 1
        # 执行
        self.execute.execute()
        # 如果run_count == 0, 则停止
        if self.run_count == 0:
            self.stop()
        # 如果run_count > 0, 则继续
        else:
            self.start()