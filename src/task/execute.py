from abc import ABC, abstractmethod

from .loader import Loader
from .execute_script.python import PythonRunner

class Execute(ABC):
    DIR = {}
    def __init__(self):
        pass

    # 注册一个执行器，用于执行某种语言的代码
    @staticmethod
    def register(execute_name):
        def wrapper(cls):
            Execute.DIR[execute_name] = cls
            return cls
        return wrapper

    @staticmethod
    def getInstance(kind, config) -> 'Execute':
        return Execute.DIR[kind](config)

    @abstractmethod
    def execute(self):
        pass

class PythonExecuteTaskConfig:
    key: str = None  # 脚本key
    location: str = None # 脚本所在位置， 本地，远程
    path: str = None # 脚本路径
    params: dict = None # 脚本运行参数
    mode: str = None  # pyc, py, 包
    def __init__(self, key, module, location, path, params):
        self.key = key
        self.location = location
        self.path = path
        self.params = params
        self.mode = module

@Execute.register("Python")
class PythonScriptExecute(Execute):
    def __init__(self, config: PythonExecuteTaskConfig):
        self.flag = False
        self.loader = Loader.getInstance(config.location, {"path": config.path, "key": config.key})
        self.execute_path = None
        self.init()
        self.config = config
        self.runner = PythonRunner.getInstance(config.mode, self.execute_path)
        self.flag = True

    def init(self):
        self.execute_path = self.loader.load()

    def execute(self):
        self.runner.run(self.config.params)



