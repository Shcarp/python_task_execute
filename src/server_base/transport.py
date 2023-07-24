
import time
from typing import Callable
from abc import ABC, abstractmethod

class Ctx(ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def server(self) -> 'WServer':
        pass
    
    @property
    @abstractmethod
    def data(self): 
        pass
    
    @property
    @abstractmethod
    def url(self):
        pass
    
    @property
    @abstractmethod
    def body(self):
        pass
    
    @property
    @abstractmethod
    def status(self):
        pass

    @body.setter
    def body(self, body):
        pass
    
    @status.setter
    def status(self, status):
        pass

    @abstractmethod
    async def send(self):
        pass

    @abstractmethod
    async def push(self, status, event, message):
        pass

class Transport(ABC):
    def __init__(self) -> None:
        self._on_message_handle = None

    async def send(self, data: any):
        await self._doSend(data)

    @abstractmethod
    def _doSend(self, data):
        pass

class WServer(ABC):
    def __init__(self) -> None:
        self.__module = {}
        self.__handleDirectory = {}

    def __getattr__(self, name):
        if (name in self.__module):
            return self.__module[name]
        else:
            raise AttributeError("module {} not found".format(name))

    
    def registerHandle(self, identification):
        '''
            注册处理函数
        '''
        def decorator(func: Callable[[Ctx], None]):
            handles = self.__handleDirectory.get(identification, [])
            handles.append(func)
            self.__handleDirectory[identification] = handles
            return func
        return decorator

    def addModule(self, name, module):
        # 改造成装饰器
        '''
            添加模块
        '''
        self.__module[name] = module

    async def _getHandles(self, identification):
        '''
            获取处理函数
        '''
        return self.__handleDirectory.get(identification, [])

    @abstractmethod
    async def handleConnect(self, socket: any):
        '''
            处理连接
        '''
        pass

    @abstractmethod
    async def run(self, port = 9673):
        '''
           启动服务
        '''
        pass
    
    @abstractmethod
    async def send(self, socket: any, status, event, message):
        '''
            发送消息
        '''
        pass
        
    @abstractmethod
    async def broadcast(self, status, event, message):
        '''
            推送消息
        '''
        pass
