import os
import threading
import time
import uuid

import schedule
from execute import Execute, PythonExecuteTaskConfig
from trigger import Trigger

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
    screen: bool = False

    def __init__(self, name, run_count, run_status, trigger_type, trigger_info, execute_type, execute_info, screen=False):
        self.name = name
        self.run_count = run_count
        self.run_status = run_status
        self.trigger_type = trigger_type
        self.trigger_info = trigger_info
        self.execute_type = execute_type
        self.execute_info = execute_info
        self.screen = screen

class Task:
    def __init__(self, config: TaskConfig):
        self.id = str(uuid.uuid4())
        self.name = config.name
        self.screen = config.screen
        self.run_count = config.run_count
        self.run_status = config.run_status
        self.trigger = Trigger.getInstance(kind=config.trigger_type, params=config.trigger_info)
        self.executer = Execute.getInstance(kind=config.execute_type, config=config.execute_info)

    # 添加task_manage的引用
    def add_task_manage(self, task_manage):
        self.task_manage = task_manage

    def start(self):
        self.trigger.monitor(self)
        # 设置状态为运行中
        self.run_status = 1

    def stop(self):
        self.trigger.stop()
        # 设置状态为停止
        self.run_status = 0
    
    def execute(self):
        # run_count 减少
        self.run_count -= 1
        # 执行
        th = threading.Thread(target=self.executer.execute)
        th.start()
        # 如果run_count == 0, 则停止
        if self.run_count == 0:
            th.join()
            self.stop()

def testTrigger():
    task = Task(config=TaskConfig(
            name="test", 
            run_count=5, 
            run_status=0, 
            trigger_type="interval", 
            trigger_info={"interval": 4}, 
            execute_type="Python", 
            execute_info=PythonExecuteTaskConfig(
                key="test.zip",
                module="py",
                location="local",
                path=os.path.join(os.getcwd(), "task","__test__", "test.zip"),
                params={"a": 1, "b": 2}
            )
        )
    )
    task.start()

    task = Task(config=TaskConfig(
            name="test", 
            run_count=5, 
            run_status=0, 
            trigger_type="interval", 
            trigger_info={"interval": 4}, 
            execute_type="Python", 
            execute_info=PythonExecuteTaskConfig(
                key="7339de53cee41af98a2109200.0.1.tar.gz",
                module="package",
                location="remote",
                path="http://1.117.56.86:8090/download/7339de53cee41af98a2109200.0.1.tar.gz",
                params={"a": 1, "b": 3}
            )
        )
    )
    task.start()

    while True:
        schedule.run_pending()
        time.sleep(1)


# testTrigger()