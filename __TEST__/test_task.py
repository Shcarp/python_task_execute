import os
import sys
import time
import schedule
sys.path.append(os.path.join(os.getcwd()))
print(sys.path)

from src.task.base import Task, TaskConfig
from src.task.execute import PythonExecuteTaskConfig

def testTrigger():
    task = Task(config=TaskConfig(
            name="test", 
            run_count=5, 
            trigger_type="interval", 
            trigger_info={"interval": 4}, 
            execute_type="Python", 
            execute_info=PythonExecuteTaskConfig(
                key="test.zip",
                module="py",
                location="local",
                path=os.path.join(os.getcwd(), '__test__', "testData", "test.zip"),
                params={"a": 1, "b": 2}
            )
        )
    )
    task.start()

    task = Task(config=TaskConfig(
            name="test", 
            run_count=5, 
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


testTrigger()