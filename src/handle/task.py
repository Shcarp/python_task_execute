import asyncio
from src.globals import server
from src.server_base.transport import Ctx
from src.server_base.wrap_pb import Status
from src.task.base import Task, TaskConfig
from src.task.execute import PythonExecuteTaskConfig

@server.registerHandle("/task/add")
async def handleAddTask(ctx: Ctx):
    # 判断name, run_count, trigger_type, trigger_info, execute_type, execute_info是否在data中
    required_keys = ["name", "run_count", "trigger_type", "trigger_info", "execute_type", "execute_info"]

    for key in required_keys:
        if key not in ctx.data:
            ctx.status = Status.BAD_REQUEST
            ctx.body = f"{key} not in data"
            await ctx.send()
            return    
    
    # 判断 key, module, location, path, params是否在execute_info中
    required_keys = ["key", "module", "location", "path", "params"]
    
    for key in required_keys:
        if key not in ctx.data["execute_info"]:
            ctx.status = Status.BAD_REQUEST
            ctx.body = f"{key} not in execute_info"
            await ctx.send()
            return
        
    # 从data中获取参数
    name = ctx.data["name"]
    run_count = ctx.data["run_count"]
    trigger_type = ctx.data["trigger_type"]
    trigger_info = ctx.data["trigger_info"]
    execute_type = ctx.data["execute_type"]
    execute_info = ctx.data["execute_info"]

    # 从execute_info中获取参数
    key = execute_info["key"]
    module = execute_info["module"]
    location = execute_info["location"]
    path = execute_info["path"]
    params = execute_info["params"]

    task = Task(config=TaskConfig(
                name=name, 
                run_count=run_count, 
                trigger_type=trigger_type,
                trigger_info=trigger_info, 
                execute_type=execute_type, 
                execute_info=PythonExecuteTaskConfig(
                    key=key,
                    module=module,
                    location=location,
                    path=path,
                    params=params
                )
            )
        )
    try:
        await task.init()
        ctx.server.task_manage.add(task)
        ctx.status = Status.OK
        ctx.body = task.id
        await ctx.send()
    except:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "fail"
        await ctx.send()

@server.registerHandle("/task/start")
async def handleStartTask(ctx: Ctx):
    if "task_id" not in ctx.data:
        ctx.status = Status.BAD_REQUEST
        ctx.body = "task_id not in data"
        await ctx.send()
        return
    task_id = ctx.data["task_id"]
    try:
        await ctx.server.task_manage.start(task_id)
        ctx.status = Status.OK
        ctx.body = "success"
        await ctx.send()
    except:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "fail"
        await ctx.send()

@server.registerHandle("/task/stop")
async def handleStopTask(ctx: Ctx):
    if "task_id" not in ctx.data:
        ctx.status = Status.BAD_REQUEST
        ctx.body = "task_id not in data"
        await ctx.send()
        return
    task_id = ctx.data["task_id"]
    try:
        ctx.server.task_manage.stop(task_id)
        ctx.status = Status.OK
        ctx.body = "success"
        ctx.send()
    except:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "fail"
        await ctx.send()

@server.registerHandle("/task/remove")
async def handleRemoveTask(ctx: Ctx):
    if "task_id" not in ctx.data:
        ctx.status = Status.BAD_REQUEST
        ctx.body = "task_id not in data"
        await ctx.send()
        return
    task_id = ctx.data["task_id"]
    try:
        ctx.server.task_manage.remove(task_id)
        ctx.status = Status.OK
        ctx.body = "success"
        await ctx.send()
    except:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "fail"
        await ctx.send()

@server.registerHandle("/task/list")
async def handleListTask(ctx: Ctx):
    print(ctx.data)
    try:
        tasks = ctx.server.task_manage.get_task_list(ctx.data)
        ctx.status = Status.OK
        ctx.body = tasks
        await ctx.send()
    except Exception as e:
        print(e)
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "fail"
        await ctx.send()
