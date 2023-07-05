import os
import random
import sys
import time
import schedule

sys.path.append(os.path.join(os.getcwd()))

from src.task.base import Task, TaskConfig
from src.task.execute import PythonExecuteTaskConfig

def generateTask(run_count, time, param):
    return Task(config=TaskConfig(
            name="test" + str(param["a"]), 
            block=True,
            run_count=run_count, 
            trigger_type="interval", 
            trigger_info={"interval": time}, 
            execute_type="Python", 
            execute_info=PythonExecuteTaskConfig(
                key="test.zip",
                module="py",
                location="local",
                path=os.path.join(os.getcwd(), '__test__', "testData", "test.zip"),
                params=param
            )
        )
    )

def testTrigger():
    taskList = []

    for i in range(0, 50):
        print(i)
        task = generateTask(1, 1, {"a": i, "b": i})
        taskList.append(task)
        task.start()


    while True:
        schedule.run_pending()
        time.sleep(1)


testTrigger()