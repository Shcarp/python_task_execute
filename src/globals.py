import asyncio
from src.server_base.wrap_pb import InfoType
from src.service.wobsocket import WebSocketServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler

loop = asyncio.new_event_loop()

def get_loop():
    return loop

server = WebSocketServer()

scheduler: AsyncIOScheduler = AsyncIOScheduler(loop=loop)

class Info:
    status: InfoType = InfoType.SUCCESS,
    body = None
    def __init__(self, message: any) -> None:
        self.body = message

class Success(Info):
    def __init__(self, message: any) -> None:
        super().__init__(message)
        self.status = InfoType.SUCCESS

class Error(Info):
    def __init__(self, message: any) -> None:
        super().__init__(message)
        self.status = InfoType.ERROR

class Warn(Info):
    def __init__(self, message: any) -> None:
        super().__init__(message)
        self.status = InfoType.WARN

