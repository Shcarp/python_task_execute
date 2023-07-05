import os
import random
import sys

sys.path.append(os.path.join(os.getcwd()))

from src.task.base import Task, TaskConfig
from src.task.execute import PythonExecuteTaskConfig

def generateTask(run_count, time):
    return Task(config=TaskConfig(
            name="test", 
            run_count=run_count, 
            trigger_type="interval", 
            trigger_info={"interval": time}, 
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

def testTrigger():
    taskList = []

    for i in range(1, 10):
        task = generateTask(5, i + random.randint(1, 10))
        taskList.append(task)
    
    for task in taskList:
        print(task.serialize())


testTrigger()