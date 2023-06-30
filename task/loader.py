from abc import ABC, abstractmethod
import os
from globals import run_path
import requests

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
    def getInstance(kind, params) -> "Loader":
        return Loader.dir[kind](params)
    
    @abstractmethod
    def load(self) -> str:
        pass

@Loader.register("local")
class LocalLoader(Loader):
    def __init__(self, params):
        self.name = params.get("key")
        self.path = params.get("path")
        pass

    async def load(self) -> str:
        # 将文件读取然后写入到SCRIPT_CACHE文件夹中
        l_path = os.path.join(run_path, "SCRIPT_CACHE", self.key)
        with open(self.path, "r") as f:
            with open(l_path, "w") as l_f:
                l_f.write(f.read())
                l_f.close()
            f.close()
        return l_path

@Loader.register("remote")
class RemoteLoader(Loader):
    def __init__(self, params):
        self.name = params.get("key")
        self.path = params.get("path")
        pass

    def load(self) -> str:
        # 请求获取文件然后写入到SCRIPT_CACHE文件夹中
        res = requests.get(self.path)
        # TODO: 写入cache 文件夹
        # 从path中提取文件名
        l_path = os.path.join(run_path, "SCRIPT_CACHE", self.key) 
        
        with open(l_path, "wb") as f:
            f.write(res.content)
            f.close()
        return l_path
