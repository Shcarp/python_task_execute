from src.server_base.wrap_pb import InfoType
from src.service.wobsocket import WebSocketServer

server = WebSocketServer()

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

