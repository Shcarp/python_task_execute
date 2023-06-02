from globals import Success, Error, Warn, info_queue
from service.wrap_pb import InfoType

info_type = {
    InfoType.SUCCESS: Success,
    InfoType.ERROR: Error,
    InfoType.WARN: Warn
}

def push(status: InfoType, body: any):
    classConstructor = info_type[status]
    info_queue.put_nowait(classConstructor(body))
