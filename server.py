from module import register
from run_task import init_task
from task import addTask, editTask, getTaskList, updateTaskStatus
from module.mysql import TaskMySql, WechatNamesMySql
from wx import addWxName, getWxNameList;

from globals import get_loop, task_queue, server

async def init_task(server, regsitertime, task_module):
    task_list = await task_module.get_all_status_task("progress")
    async def callback(event, message):
        await server.push({
            "event": event,
            "data": message
        })

    for item in task_list:
        regsitertime.add({
            "id": item[0],
            "name": item[1],
            "type": item[2],
            "time": item[4],
            "content": item[5],
            "member": item[6].split(","),
            "callback": callback
        })

def run_server(regsitertime):
    loop = get_loop()
    pool = loop.run_until_complete(register())

    task_module = TaskMySql(pool)
    wechat_name_module = WechatNamesMySql(pool)

    async def init_task_func(task_module):
        server.addModule("task", task_module)
        await init_task(server, regsitertime, task_module)
    
    async def init_wechat_name_func(wechat_name_module):
        server.addModule("wechat", wechat_name_module)

    loop.run_until_complete(task_module.init_sql(init_task_func))
    loop.run_until_complete(wechat_name_module.init_sql(init_wechat_name_func))

    server.addModule("registerTime", regsitertime)

    server.registerHandle("/task/list", getTaskList)
    server.registerHandle("/task/add", addTask)
    server.registerHandle("/task/edit", editTask)
    server.registerHandle("/task/update", updateTaskStatus)

    server.registerHandle("/wxuser/add", addWxName)
    server.registerHandle("/wxuser/list", getWxNameList)

    server.registerHandle("/task-size", task_queue.qsize)
    
    loop.run_until_complete(server.run())
