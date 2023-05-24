import asyncio
import json
import os
import websockets
from typing import Callable
from websockets.server import serve

# from utils import parse_json

class Ctx:
    __send = 0
    __socket = None
    __sequence = 0
    __serve = None

    __data = None
    __body = None
    __status = 200

    def __init__(self, serve, sequence, data, socket) -> None:
        self.__serve = serve
        self.__sequence = sequence
        self.__data = data
        self.__socket = socket

    @property
    def serve(self):
        return self.__serve
    
    @property
    def data(self): 
        return self.__data
    
    @property
    def url(self):
        return self.data["url"]
    
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
        recvData = {
            "type": "response",
            "sequence": self.__sequence,
            "status": self.__status,
            "data": self.__body
        }
        await self.__socket.send(json.dumps(recvData))
        self.__send = 1
    
    async def push(self, message):
        recvData = {
            "type": "push",
            "status": 200,
            "data": message
        }
        await self.__socket.send(json.dumps(recvData))


class WebSocketConnection:
    __socket = None
    __serve = None
    
    def __init__(self, serve, socket):
        self.__serve = serve
        self.__socket = socket

    @property
    def socket(self):
        return self.__socket

    async def handleMessage(self):
        async for data in self.socket:
            print(data)
            pdata = json.loads(data)
            ctx = Ctx(self.__serve, pdata["sequence"], pdata["data"]["data"], self.socket)
            handles = await self.__serve.getHandles(pdata["data"]["url"])
            print(handles)
            for handle in handles:
                await handle(ctx)

    async def push(self, message):
        recvData = {
            "type": "push",
            "status": 200,
            "data": message
        }
        await self.__socket.send(json.dumps(recvData))

class WebSocketServer:
    __port = 9673
    __connections = set()
    __CONNECT = set()

    __module = {}
    __handleDirectory = {}

    def __getattr__(self, name):
        if (name in self.__module):
            return self.__module[name]
        else:
            raise AttributeError("module {} not found".format(name))

    def __init__(self, port):
        self.__port = port if port is not None else self.port

    async def run(self):
        '''
           启动服务
        '''
        print("server run, port: {}, pid: {}".format(self.__port, os.getpid()))
        async with serve(self.handleConnect, "", self.__port):
            await asyncio.Future()
        
    def registerHandle(self, identification, func: Callable[[Ctx], None]):
        '''
            注册处理函数
        '''
        handles = self.__handleDirectory.get(identification, [])
        handles.append(func)
        self.__handleDirectory[identification] = handles

    def addModule(self, name, module):
        '''
            添加模块
        '''
        self.__module[name] = module

    async def getHandles(self, identification):
        '''
            获取处理函数
        '''
        return self.__handleDirectory.get(identification, [])

    async def handleConnect(self, websocket):
        '''
            处理连接
        '''
        connection = WebSocketConnection(self, websocket)
        self.__connections.add(connection)
        self.__CONNECT.add(websocket)
        try:
            await connection.handleMessage()
            await websocket.await_closed()
        except Exception as e:
            print(e)
        finally:
            self.__connections.remove(connection)
            self.__CONNECT.remove(websocket)
        
    
    async def push(self, message):
        '''
            推送消息
        '''
        recvData = {
            "type": "push",
            "status": 200,
            "data": message
        }

        websockets.broadcast(self.__CONNECT, json.dumps(recvData))
