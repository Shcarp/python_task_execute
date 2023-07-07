import asyncio
from threading import Thread
import src.handle.task
from src.globals import server, scheduler, loop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.task.task_manage import TaskManage

async def run_scheduler():
    scheduler.start()

async def run_server():
    # scheduler.start()
    # 启动任务管理器
    task_manage = TaskManage()
    server.addModule("task_manage", task_manage)
    # 启动服务
    await server.run(loop=loop)
def main():
    async def run():
        await asyncio.gather(run_scheduler(), run_server())
    # 启动websocket服务
    try:
        loop.run_until_complete(run())
    except Exception as e:
        print(e)

    finally:
        loop.close()
