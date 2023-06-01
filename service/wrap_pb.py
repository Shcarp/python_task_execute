
from enum import Enum
import json
from typing import Any
from service import message_pb2 as pb

class DataType(Enum):
    NUMBER = pb.DataType.number
    STRING = pb.DataType.string
    FLOAT = pb.DataType.float
    JSON = pb.DataType.json

class InfoType(Enum):
    SUCCESS = pb.InfoType.SUCCESS
    ERROR = pb.InfoType.ERROR
    WARN = pb.InfoType.WARN

class Status(Enum):
    UNKNOW = pb.Status.UNKNOW
    OK = pb.Status.OK
    BAD_REQUEST = pb.Status.BAD_REQUEST
    NOT_FOUND = pb.Status.NOT_FOUND
    INTERNAL_SERVER_ERROR = pb.Status.INTERNAL_SERVER_ERROR  

class Request:
    url: str = None
    type: str = 'request'
    sequence: str = None
    sendTime: int = None
    data: Any = None

    def __init__(self, url, sequence, sendTime, data) -> None:
        self.url = url
        self.sequence = sequence
        self.sendTime = sendTime

        if (data.type == pb.DataType.JSON):
            self.data = json.loads(data.value)
        elif (data.type == pb.DataType.NUMBER):
            self.data = int(data.value)
        elif (data.type == pb.DataType.FLOAT):
            self.data = float(data.value)
        else:
            self.data = data.value

    @staticmethod
    def parse(str):
        request = pb.Request()
        request.ParseFromString(str)
        return Request(request.url, request.sequence, request.sendTime, request.data)

class Response:
    type: str = 'response'
    sequence: str = None
    status: Status = None
    sendTime: int = None
    data: Any = None

    def __init__(self, sequence, status, sendTime, data) -> None:
        self.sequence = sequence
        self.status = status
        self.sendTime = sendTime
        self.data = data

    def serialize(self):
        response = pb.Response()
        response.type = self.type
        response.sequence = self.sequence
        response.status = self.status
        response.sendTime = self.sendTime

        def assignment(type, data):
            body = pb.Body()
            body.type = type
            body.value = data 
            response.data.CopyFrom(body)

        if (type(self.data) == dict or type(self.data) == list):
            assignment(DataType.JSON.value, json.dumps(self.data))
        elif (type(self.data) == int):
            response.data.value = str(self.data)
        elif (type(self.data) == float):
            assignment(DataType.FLOAT.value, str(self.data))
        else:
            assignment(DataType.STRING.value, self.data)

        return response.SerializeToString()

class Push:
    type: str = 'push'
    event: str = None
    status: Status = None
    sendTime: int = None
    data: Any = None

    def __init__(self, event, status, sendTime, data) -> None:
        self.event = event
        self.status = status
        self.sendTime = sendTime
        self.data = data

    def serialize(self):
        push = pb.Push()
        push.type = self.type
        push.event = self.event
        push.status = self.status.value
        push.sendTime = self.sendTime

        def assignment(type, data):
            body = pb.Body()
            body.type = type
            body.value = data 
            push.data.CopyFrom(body)

        if (type(self.data) == dict or type(self.data) == list):
            assignment(DataType.JSON.value, json.dumps(self.data))
        elif (type(self.data) == int):
            assignment(DataType.NUMBER.value, str(self.data))
        elif (type(self.data) == float):
            assignment(DataType.FLOAT.value, str(self.data))
        else:
            assignment(DataType.STRING.value, self.data)

        return push.SerializeToString()
