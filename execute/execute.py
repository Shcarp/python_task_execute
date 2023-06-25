from abc import ABC, abstractmethod

from importlib.util import module_from_spec, spec_from_file_location
import os

from task import ExecuteTaskConfig

class Loader(ABC):
    dir = {}
    def __init__(self):
        pass

    @staticmethod
    def register(loader_name):
        def wrapper(cls):
            Loader.dir[loader_name] = cls
            return cls
        return wrapper
    
    @staticmethod
    def getInstance(kind):
        return Loader.dir[kind]()
    
    @abstractmethod
    def loader_source_code(self, path) -> str:
        pass

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
    def getInstance(kind):
        return Execute.dir[kind]()

    @abstractmethod
    def execute(self, path):
        pass

@Loader.register("local")
class PycLoader(Loader):
    def __init__(self):
        pass

    def loader_source_code(self, path) -> str:
        return path

@Execute.register("pyc")
class PycExecute(Execute):
    def __init__(self):
        pass

    def execute(self, path):
                # 提取文件名
        module_name = os.path.basename(path).split(".")[0]

        spec = spec_from_file_location(module_name, path)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

# 开始一个任务需要一个加载器和一个执行器
class Task:
    loader: Loader = None
    execute: Execute = None
    def __init__(self, config: ExecuteTaskConfig):
        module_k= os.path.basename(config.path).split(".")[-1]
        self.origin_path = config.path
        self.loader = Loader.getInstance(config.location)
        self.execute = Execute.getInstance(module_k)

    def run(self):
        path = self.loader.loader_source_code(self.origin_path)
        module = self.execute.execute(path=path)
        res = module.run()  
        return res

def test():
    task = Task(ExecuteTaskConfig(
        name="test",
        location="local",
        path="./cache/test.pyc",
        params={}
    ))
    task.run()
