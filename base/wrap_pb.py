
from enum import Enum
import json
from typing import Any
from base import message_pb2 as pb

class MessageType(Enum):
    OTHER = b'0'
    PUSH = b'1'
    REQUEST = b'2'
    RESPONSE = b'3'

class DataType(Enum):
    STRING = pb.DataType.String
    NUMBER = pb.DataType.Number
    BOOL = pb.DataType.Bool
    ARRAY = pb.DataType.Array
    OBJECT = pb.DataType.Object
    NULL = pb.DataType.Null
    

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

        if (data.type == DataType.ARRAY.value):
            self.data = json.loads(data.value)
        elif (data.type == DataType.NUMBER.value):
            self.data = int(data.value)
        elif (data.type == DataType.BOOL.value):
            self.data = bool(data.value)
        elif (data.type == DataType.OBJECT.value):
            self.data = json.loads(data.value)
        elif (data.type == DataType.NULL.value):
            self.data = None
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
        response.status = self.status.value
        response.sendTime = self.sendTime

        def assignment(type, data):
            body = pb.Body()
            body.type = type
            body.value = data 
            response.data.CopyFrom(body)

        if (type(self.data) == dict):
            assignment(DataType.OBJECT.value, json.dumps(self.data))
        elif (type(self.data) == list):
            assignment(DataType.ARRAY.value, json.dumps(self.data))
        elif (type(self.data) == int):
            assignment(DataType.NUMBER.value, str(self.data))
        elif (type(self.data) == bool):
            assignment(DataType.BOOL.value, str(self.data))
        elif (type(self.data) == str):
            assignment(DataType.STRING.value, self.data)
        elif (self.data == None):
            assignment(DataType.NULL.value, None)
        else:
            raise Exception("data type error")
        


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

        if (type(self.data) == dict):
            assignment(DataType.OBJECT.value, json.dumps(self.data))
        elif (type(self.data) == list):
            assignment(DataType.ARRAY.value, json.dumps(self.data))
        elif (type(self.data) == int):
            assignment(DataType.NUMBER.value, str(self.data))
        elif (type(self.data) == bool):
            assignment(DataType.BOOL.value, str(self.data))
        elif (type(self.data) == str):
            assignment(DataType.STRING.value, self.data)
        elif (self.data == None):
            assignment(DataType.NULL.value, None)
        else:
            raise Exception("data type error")
        
        return push.SerializeToString()
