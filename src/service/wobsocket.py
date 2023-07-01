import asyncio
import os
import time
import websockets
from websockets.server import serve, WebSocketServerProtocol
from src.server_base.transport import Ctx, WServer, Transport
from src.server_base.wrap_pb import MessageType, Push, Request

class WebSocketTransport(Transport):
    def __init__(self, socket):
        self.__socket = socket

    async def _doSend(self, data):
       await self.__socket.send(data)

class WebSocketServer(WServer):
    __CONNECT = set()

    async def run(self, port = 9673):
        '''
           启动服务
        '''
        print("server run, port: {}, pid: {}".format(port, os.getpid()))
        async with serve(self.handleConnect, "", port):
            await asyncio.Future()
    
    async def handleConnect(self, socket: WebSocketServerProtocol):
        '''
            处理连接
        '''
        self.__CONNECT.add(socket)
        transport = WebSocketTransport(socket)
        try:
            async for data in socket:
                if isinstance(data, bytes) == False:
                    transport.send("data type error")
                    continue
                index = 0
                if ( data[index:1] == MessageType.REQUEST.value):
                    index += 1
                    request: Request = Request.parse(data[index:])
                    ctx = Ctx(self, transport, request)
                    handles = await self._getHandles(request.url)
                    if (handles == None):
                        continue
                    for handle in handles:
                        await handle(ctx)
        except Exception as e:
            print("server error: {}".format(e))
        # finally: 
            # self.__CONNECT.remove(socket)
    
    async def pushSingle(self, socket: any, status, event, message):
        '''
            发送消息
        '''
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message).serialize()
        await socket.send(sendData)

    async def push(self, status, event, message):
        '''
            推送消息
        '''
        sendData = MessageType.PUSH.value +  Push(status=status, sendTime=time.time(), event=event, data=message).serialize()
        
        websockets.broadcast(self.__CONNECT, sendData)
