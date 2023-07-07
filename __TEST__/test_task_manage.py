import os
import sys
sys.path.append(os.path.join(os.getcwd()))
from src.task.task_manage import TaskManage
from src.task.base import Task, TaskConfig
from src.task.execute import PythonExecuteTaskConfig

'''
    测试, 在关闭了executor的情况下, taskManage的状态
'''

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

taskManage = TaskManage()


task1id = taskManage.add(generateTask(5, 1))

assert len(taskManage.get_all_list()) == len(taskManage.get_no_start_list())

taskManage.start(task1id)

assert len(taskManage.get_all_list()) == 1
assert len(taskManage.get_no_start_list()) == 0
assert len(taskManage.get_running_list()) == 1

taskManage.cancel(task1id)

assert len(taskManage.get_all_list()) == 1
assert len(taskManage.get_no_start_list()) == 1
assert len(taskManage.get_running_list()) == 0

taskManage.remove(task1id)

assert len(taskManage.get_all_list()) == 0
assert len(taskManage.get_no_start_list()) == 0
assert len(taskManage.get_running_list()) == 0

# 添加10个
taskList = []
for i in range(0, 10):
    taskList.append(taskManage.add(generateTask(5, i)))

assert len(taskManage.get_all_list()) == len(taskManage.get_no_start_list())

# 启动5个
for i in range(0, 5):
    taskManage.start(taskList[i])

assert len(taskManage.get_all_list()) == len(taskList)
assert len(taskManage.get_no_start_list()) == len(taskList) - 5
assert len(taskManage.get_running_list()) == 5

# 停止2个
for i in range(0, 2):
    taskManage.cancel(taskList[i])

assert len(taskManage.get_all_list()) == len(taskList)
assert len(taskManage.get_no_start_list()) == len(taskList) - 3
assert len(taskManage.get_running_list()) == 3

# 开启最后两个
for i in range(8, 10):
    taskManage.start(taskList[i])

# 完成 最后两个
for i in range(8, 10):
    taskManage.complete(taskList[i])

# 开启倒数第三个
taskManage.start(taskList[7])

# 发生错误
taskManage.error(taskList[7])

assert len(taskManage.get_all_list()) == len(taskList)

assert len(taskManage.get_no_start_list()) == 4
assert len(taskManage.get_running_list()) == 3
assert len(taskManage.get_error_list()) == 1
assert len(taskManage.get_complete_list()) == 2

# 删除一个
taskManage.remove(taskList[0])

assert len(taskManage.get_all_list()) == len(taskList) - 1
assert len(taskManage.get_no_start_list()) == 3
assert len(taskManage.get_running_list()) == 3
