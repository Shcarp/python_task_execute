import asyncio
import os
import time
from requests import Response
import websockets
from websockets.server import serve, WebSocketServerProtocol
from src.server_base.transport import Ctx, WServer, Transport
from src.server_base.wrap_pb import MessageType, Push, Request


class WebsocketCtx(Ctx):
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


class WebSocketTransport(Transport):
    def __init__(self, socket):
        super().__init__()
        self.__socket = socket

    async def _doSend(self, data):
       await self.__socket.send(data)

class WebSocketServer(WServer):
    def __init__(self):
        super().__init__()
        self. __CONNECT = set()

    async def run(self, port = 9673, loop = None):
        '''
           启动服务
        '''
        print("server run, port: {}, pid: {}".format(port, os.getpid()))
        async with serve(self.handleConnect, "", port):
            await asyncio.Future(loop=loop)
    
    async def handleConnect(self, socket: WebSocketServerProtocol):
        '''
            处理连接
        '''
        self.__CONNECT.add(socket)
        transport = WebSocketTransport(socket)

        try:
            async for data in socket:
                print("server receive: {}".format(data))
                if isinstance(data, bytes) == False:
                    await transport.send("data type error")
                    continue
                index = 0
                if ( data[index:1] == MessageType.REQUEST.value):
                    index += 1
                    request: Request = Request.parse(data[index:])
                    ctx = WebsocketCtx(self, transport, request)
                    handles = await self._getHandles(request.url)
                    if (handles == None):
                        continue
                    for handle in handles:
                        await handle(ctx)
        except Exception as e:
            print("server error: {}".format(e))
    
    async def send(self, socket: any, status, event, message):
        '''
            发送消息
        '''
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message).serialize()
        await socket.send(sendData)

    async def broadcast(self, status, event, message):
        '''
            推送消息
        '''
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message).serialize()
        
        websockets.broadcast(self.__CONNECT, sendData)
