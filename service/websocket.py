import asyncio
import os
import time
from service.wrap_pb import MessageType, Push, Request, Response
import websockets
from typing import Callable
from websockets.server import serve, WebSocketServerProtocol 

class Ctx:
    __send = 0
    __socket: WebSocketServerProtocol = None
    __serve: 'WebSocketServer' = None

    __request: Request = None

    __body = None
    __status = 200

    def __init__(self, serve, socket, request: Request) -> None:
        self.__serve = serve
        self.__socket = socket
        self.__request = request

    @property
    def serve(self):
        return self.__serve
    
    @property
    def data(self): 
        return self.__request.data.value
    
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
        response = MessageType.RESPONSE.value +  Response(self.__request.sequence, self.__status, time.time(), self.__body)
        await self.__socket.send(response.serialize())
        self.__send = 1
    
    async def push(self, status, event, message):
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message)
        await self.__socket.send(sendData.serialize())


class WebSocketConnection:
    __socket: WebSocketServerProtocol = None
    __serve: 'WebSocketServer' = None
    
    def __init__(self, serve, socket):
        self.__serve = serve
        self.__socket = socket

    @property
    def socket(self):
        return self.__socket

    async def handleMessage(self):
        async for data in self.socket:
            if isinstance(data, bytes) == False:
                self.socket.send("data type error")
                continue
            index = 0
            if (data[index] == MessageType.REQUEST.value):
                index += 1
                request: Request = Request.parse(data[index:])
                ctx = Ctx(self.__serve, self.socket, request)
                handles = await self.__serve.getHandles(request.url)
                if (handles == None):
                    continue
                for handle in handles:
                    await handle(ctx)

    async def push(self, status, event, message):
        push = MessageType.PUSH.value +  Push(status=status, sendTime=time.time() ,event=event, data=message)
        await self.__socket.send(push.serialize())

class WebSocketServer:
    __connections = set()
    __CONNECT = set()

    __module = {}
    __handleDirectory = {}

    def __getattr__(self, name):
        if (name in self.__module):
            return self.__module[name]
        else:
            raise AttributeError("module {} not found".format(name))

    async def run(self, port = 9673):
        '''
           启动服务
        '''
        print("server run, port: {}, pid: {}".format(port, os.getpid()))
        async with serve(self.handleConnect, "", port):
            await asyncio.Future()
        
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

    async def getHandles(self, identification):
        '''
            获取处理函数
        '''
        return self.__handleDirectory.get(identification, [])

    async def handleConnect(self, websocket: WebSocketServerProtocol):
        '''
            处理连接
        '''
        connection = WebSocketConnection(self, websocket)
        self.__connections.add(connection)
        self.__CONNECT.add(websocket)
        try:
            await connection.handleMessage()
        except Exception as e:
            print("server error: {}".format(e))
        finally: 
            self.__connections.remove(connection)
            self.__CONNECT.remove(websocket)
    
    async def pushSingle(self, websocket: WebSocketServerProtocol, status, event, message):
        '''
            发送消息
        '''
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time() ,event=event, data=message).serialize()

        await websocket.send(sendData)
        
    
    async def push(self, status, event, message):
        '''
            推送消息
        '''

        sendData = MessageType.PUSH.value + Push(status=status, sendTime=time.time(), event=event, data=message).serialize()

        websockets.broadcast(self.__CONNECT, sendData)
