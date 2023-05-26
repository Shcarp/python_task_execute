
from enum import Enum
import json

class InfoType(Enum):
    Success = 0
    ERROR = 1
    WARN = 2

class Status(Enum):
    WARN = 100
    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

        
PUBLIC_ENUMS = {
    'InfoType': InfoType,
    'Status': Status
}

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return obj.value
        return json.JSONEncoder.default(self, obj)

def enum_hook(obj):
    for name, member in PUBLIC_ENUMS.items():
        if obj == member.value:
            return member
    return obj

class Request:
    url: str = None
    ctype: str = 'request'
    sequence: str = None
    sendTime: int = None
    data: any = None

    def __init__(self, url, sequence, sendTime, data) -> None:
        self.url = url
        self.sequence = sequence
        self.sendTime = sendTime
        self.data = data

    # 序列化为json
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    # 反序列化
    @staticmethod
    def fromJSON(jsonStr) -> 'Request':
        try:
            obj = json.loads(jsonStr)
            return Request(**obj)
        except Exception as e:
            print("error: {}".format(e))
            return Request(
                url=None,
                sequence=None,
                sendTime=None,
                data=None
            )

class Response:
    ctype: str = 'response'
    sequence: str = None
    status: Status = Status.OK
    sendTime: int = None
    data: any = None

    def __init__(self, sequence, status, sendTime, data) -> None:
        self.sequence = sequence
        self.status = status
        self.sendTime = sendTime
        self.data = data

    # 序列化为json
    def toJSON(self):
        try:
            return json.dumps({
                'ctype': self.ctype,
                'sequence': self.sequence,
                'status': self.status,
                'sendTime': self.sendTime,
                'data': self.data
            }, cls=EnumEncoder)
        except Exception as e:
            return Response(
                type=self.type,
                sequence=self.sequence, 
                status=Status.INTERNAL_SERVER_ERROR, 
                sendTime=self.sendTime, 
                data='format error: {}'.format(e)
            ).toJSON()

    # 反序列化
    @staticmethod
    def fromJSON(jsonStr):
        try:
            obj = json.loads(jsonStr, object_hook=enum_hook)
            return Response(**obj)
        except Exception as e:
            print("format error: {}".format(e))
            return 
        
class Push:
    ctype: str = 'push'
    event: str = None
    status: InfoType = None
    sendTime: int = None
    data: any = None

    def __init__(self, status, sendTime, event, data) -> None:
        self.event = event
        self.status = status
        self.sendTime = sendTime
        self.data = data

    # 序列化为json
    def toJSON(self):
        try:
            return json.dumps({
                'ctype': self.ctype,
                'event': self.event,
                'status': self.status,
                'sendTime': self.sendTime,
                'data': self.data
            }, cls=EnumEncoder)
        except Exception as e:
            print("format error: {}".format(e))
            return Push(
                status=InfoType.ERROR, 
                sendTime=self.sendTime, 
                event=self.event,
                data='format error: {}'.format(e)
            ).toJSON()

    # 反序列化
    @staticmethod
    def fromJSON(jsonStr):
        try:
            obj = json.loads(jsonStr, object_hook=enum_hook)
            return Push(**obj)
        except Exception as e:
            print("format error: {}".format(e))
            return


