import asyncio
from src.globals import server

async def run_server():
    await server.run()

def main():
    # 启动websocket服务
    asyncio.run(run_server())


