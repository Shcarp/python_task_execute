
import re
from .base import Task

class TaskManage:
    def __init__(self) -> None:
        # 未开始
        self.task_map = {}

    def get_Task(self, id) -> Task:
        return self.task_map[id]

    def add(self, task: Task):
        if task.id in self.task_map:
            raise Exception("task already exists")
        self.task_map[task.id] = task
        return task.id
    
    async def start(self, id):
        if id not in self.task_map:
            raise Exception("task not found")
        task: Task =self.get_Task(id)
        await task.start()

    def cancel(self, id):
        if id not in self.task_map:
            raise Exception("task not found")
        task = self.get_Task(id)
        task.cancel()
    
    def remove(self, id):
        if id not in self.no_start_dir:
            raise Exception("task not found")
        
        self.task_map.pop(id)

    def get_task_list(self, params):
        '''
            获取任务列表
            params: {
                keyword: 关键字
                status: 状态
            }
        '''
        # 从self.task_map中获取

        filtered_tasks = []

        for task in self.task_map.values():
            if 'keyword' in params and not re.search(params['keyword'], task.name, re.IGNORECASE):
                continue
            
            if 'status' in params and task.run_status != params['status']:
                continue

            filtered_tasks.append(task.serialize())

        return filtered_tasks