from abc import ABC, abstractmethod

from .serialize import Serialize

from .loader import Loader
from .execute_script.python import PythonRunner

class Execute(Serialize, ABC):
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
    async def execute(self):
        pass

    @abstractmethod
    def serialize(self):
        pass

class PythonExecuteTaskConfig:
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
        self.config = config

    async def init(self):
        self.execute_path = self.loader.load()
        self.runner = PythonRunner.getInstance(self.config.mode, self.execute_path)
        await self.runner.init()
        self.flag = True

    async def execute(self):
        return await self.runner.run(self.config.params)

    def serialize(self):
        return {
            "key": self.config.key,
            "location": self.config.location,
            "path": self.config.path,
            "params": self.config.params,
            "mode": self.config.mode,
        }
