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
                params=param
            )
        )
    )

def testTrigger():
    taskList = []

    # for i in range(0, 50):
    #     task = generateTask(1, i % 5, {"a": i, "b": i})
    #     taskList.append(task)
    #     task.start()

    for i in range(0, 50):
        task2 = Task(config=TaskConfig(
                name="test", 
                run_count=1, 
                trigger_type="interval", 
                trigger_info={"interval": 1}, 
                execute_type="Python", 
                execute_info=PythonExecuteTaskConfig(
                    key="7339de53cee41af98a2109200.0.1.tar.gz",
                    module="package",
                    location="remote",
                    path="http://1.117.56.86:8090/download/7339de53cee41af98a2109200.0.1.tar.gz",
                    params={"a": i, "b": i}
                )
            )
        )
        taskList.append(task2)

    for task in taskList:
        task.start()

    while True:
        schedule.run_pending()
        time.sleep(1)


testTrigger()