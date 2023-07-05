
from .base import Task

class TaskManage:
    def __init__(self) -> None:
        # 未开始
        self.no_start_dir = {}
        self.running_dir = {}
        self.complete_dir = {}
        self.error_dir = {}

    def add(self, task: Task):
        self.no_start_dir[task.id] = task
        task.add_task_manage(self)
        return task.id
    
    def start(self, id):
        task = self.no_start_dir.pop(id)
        task.start()
        self.running_dir[id] = task

    def stop(self, id):
        task = self.running_dir.pop(id)
        task.stop()
        self.no_start_dir[id] = task
    
    def remove(self, id):
        if id not in self.no_start_dir:
            return
        self.no_start_dir.pop(id)

    def complete(self, id):
        task = self.running_dir.pop(id)
        self.complete_dir[id] = task
    
    def error(self, id, error = "success"):
        task = self.running_dir.pop(id)
        self.error_dir[id] = task

    def get_all_list(self):
        res = []
        all_dirs = [self.no_start_dir, self.running_dir, self.complete_dir, self.error_dir]

        for task_dir in all_dirs:
            res.extend(task.serialize() for task in task_dir.values())

        return res
    
    def get_no_start_list(self):
        return [task.serialize() for task in self.no_start_dir.values()]
    
    def get_running_list(self):
        return [task.serialize() for task in self.running_dir.values()]
    
    def get_complete_list(self):
        return [task.serialize() for task in self.complete_dir.values()]
    
    def get_error_list(self):
        return [task.serialize() for task in self.error_dir.values()]
