from abc import ABC, abstractmethod
import os
import tempfile
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
        self.key = params.get("key")
        self.path = params.get("path")
        pass

    def load(self) -> str:
         # tempfile 创建一个临时文件夹
        cache_dir = os.path.join(os.getcwd(), "SCRIPT_CACHE")
        # # 将文件读取然后写入到SCRIPT_CACHE文件夹中
        l_path = os.path.join(cache_dir, self.key)
        
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        # 将self.path中的文件写入到l_path中
        with open(self.path, "rb") as f:
            content = f.read()
            f.close()
        with open(l_path, "wb") as f:
            f.write(content)
            f.close()
        return l_path

@Loader.register("remote")
class RemoteLoader(Loader):
    def __init__(self, params):
        self.key = params.get("key")
        self.path = params.get("path")
        pass

    def load(self) -> str:
        # tempfile 创建一个临时文件夹
        cache_dir = os.path.join(os.getcwd(), "SCRIPT_CACHE")
        # # 将文件读取然后写入到SCRIPT_CACHE文件夹中
        l_path = os.path.join(cache_dir, self.key)
        
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)
        # 请求获取文件然后写入到SCRIPT_CACHE文件夹中
        res = requests.get(self.path)
        
        with open(l_path, "wb") as f:
            f.write(res.content)
            f.close()
        return l_path
