from abc import ABC, abstractmethod

from task.loader import Loader
from task.script.python import PythonRunner

class Execute(ABC):
    dir = {}
    def __init__(self):
        pass

    # 注册一个执行器，用于执行某种语言的代码
    @staticmethod
    def register(execute_name):
        def wrapper(cls):
            Execute.dir[execute_name] = cls
            return cls
        return wrapper

    @staticmethod
    def getInstance(kind, config) -> 'Execute':
        return Execute.dir[kind](config)

    @abstractmethod
    def execute(self):
        pass

class PythonExecuteTaskConfig:
    key: str = None  # 脚本key
    location: str = None # 脚本所在位置， 本地，远程
    path: str = None # 脚本路径
    params: dict = None # 脚本运行参数
    mode: str = None  # pyc, py, 包
    def __init__(self, name, module, location, path, params):
        self.name = name
        self.location = location
        self.path = path
        self.params = params
        self.mode = module

@Execute.register("Python")
class PythonScriptExecute(Execute):
    def __init__(self, config: PythonExecuteTaskConfig):
        self.flag = False
        self.config = config
        self.loader = Loader.getInstance(config.location, {"path": config.path,"key": config.key})
        self.runner = PythonRunner.getInstance(config.mode, config.path)

    def init(self):
        self.loader.load()
        self.flag = True

    def execute(self):
        if not self.flag:
            self.init()
        self.runner.run(self.config.params)

