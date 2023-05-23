import asyncio

loop = None

def get_loop():
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
    return loop
