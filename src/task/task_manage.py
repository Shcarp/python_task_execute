
from .base import Task

class TaskManage: 
    
    await_block_queue = []

    complete_list = []

    await_list = []

    def __init__(self) -> None:
        pass

    def add_task(self, task: Task):
        task.add_task_manage(self)
        self.await_list.append(task)
        task.start()

    def remove_task(self, task: Task):
        task.stop()
        # 删除task, 如果task 已经触发但是在阻塞队列中, 则将其移除
        if task in self.await_block_queue:
            self.await_block_queue.remove(task)
        if task in self.await_list:
            self.await_list.remove(task)
        if task in self.complete_list:
            self.complete_list.remove(task)

