import asyncio
from src.globals import server
from src.task.task_manage import TaskManage

async def run_server():
    # 启动任务管理器
    task_manage = TaskManage()
    server.addModule("task_manage", task_manage)
    # 启动服务
    await server.run()

def main():
    # 启动websocket服务
    asyncio.run(run_server())


