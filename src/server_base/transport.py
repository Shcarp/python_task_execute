
import time
from typing import Callable
from abc import ABC, abstractmethod
from src.server_base.wrap_pb import MessageType, Push, Request, Response

class Transport(ABC):
    def __init__(self) -> None:
        self._on_message_handle = None

    async def send(self, data: any):
        await self._doSend(data)

    @abstractmethod
    def _doSend(self, data):
        pass

class Ctx:
    def __init__(self, serve, socket: Transport, request: Request) -> None:
        self.__send = 0
        self.__body = None
        self.__status = 200
        self.__serve = serve
        self.__socket = socket
        self.__request = request

    @property
    def server(self) -> 'WServer':
        return self.__serve
    
    @property
    def data(self): 
        return self.__request.data
    
    @property
    def url(self):
        return self.__request.url
    
    @property
    def body(self):
        return self.__body
    
    @property
    def status(self):
        return self.__status

    @body.setter
    def body(self, body):
        self.__body = body
    
    @status.setter
    def status(self, status):
        self.__status = status
    
    async def send(self):
        if (self.__send == 1):
            return
        response = MessageType.RESPONSE.value +  Response(self.__request.sequence, self.__status, time.time(), self.__body).serialize()
        await self.__socket.send(response)
        self.__send = 1
    
    async def push(self, status, event, message):
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message).serialize()
        await self.__socket.send(sendData)


class WServer(ABC):
    def __init__(self) -> None:
        self.__module = {}
        self.__handleDirectory = {}
        pass

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
