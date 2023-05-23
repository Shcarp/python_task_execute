from loop import get_loop
from module import register
from runTask import init_task
from service import websocket
from task import addTask, editTask, getTaskList, updateTaskStatus
from module.mysql import TaskMySql, WechatNamesMySql
from wx import addWxName, getWxNameList;

def run_server(regsitertime):
    server = websocket.WebSocketServer(9673)

    print("server run")
    loop = get_loop()

    pool = loop.run_until_complete(register())

    task_module = TaskMySql(pool)
    wechat_name_module = WechatNamesMySql(pool)

    loop.run_until_complete(task_module.init_sql())
    loop.run_until_complete(wechat_name_module.init_sql())

    loop.run_until_complete(init_task(server, regsitertime, task_module))

    server.addModule("registerTime", regsitertime)
    server.addModule("task", task_module)
    server.addModule("wechat", wechat_name_module)

    server.registerHandle("/task/list", getTaskList)
    server.registerHandle("/task/add", addTask)
    server.registerHandle("/task/edit", editTask)
    server.registerHandle("/task/update", updateTaskStatus)

    server.registerHandle("/wxuser/add", addWxName)
    server.registerHandle("/wxuser/list", getWxNameList)
    
    loop.run_until_complete(server.run())
