from globals import Success, Error, Warn, info_queue
from service.oprotocol import InfoType

info_type = {
    InfoType.Success: Success,
    InfoType.ERROR: Error,
    InfoType.WARN: Warn
}

def push(status: InfoType, body: any):
    classConstructor = info_type[status]
    info_queue.put_nowait(classConstructor(body))
