import queue
from globals import task_queue,server
from service.transport import Ctx
from service.wrap_pb import InfoType, Status
keyword = ""
status = 0

async def getTask(ctx: Ctx):
    list = await ctx.serve.task.get_task_list({
            "keyword": keyword,
            "status": status
        })
    
    # 获取所有运行中的任务
    running_task: tuple = await ctx.serve.task.get_all_status_task(2)
    # 获取数量
    running_count = len(running_task)
    res = []
    for item in list:
        res.append({
            "id": item[0],
            "name": item[1],
            "type": item[2],
            "status": item[3],
            "time": item[4],
            "content": item[5],
            "member": item[6].split(","),
        })
    return (res, running_count)

@server.registerHandle("/task/list")
async def getTaskList(ctx: Ctx):
    try:
        global status, keyword
        if ( "status" in ctx.data):
            status = ctx.data["status"]
        if ( "keyword" in ctx.data):
            keyword = ctx.data["keyword"]

        (list, running_count) = await getTask(ctx)
        ctx.status = Status.OK
        ctx.body = {
            "list": list,
            "running_count": running_count
        }
        await ctx.send()
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()

@server.registerHandle("/task/add")
async def addTask(ctx: Ctx):
    try:
        insertdata = ctx.data
        id = await ctx.serve.task.create_task(insertdata)
        ctx.status = Status.OK
        ctx.body = {
            "id": id
        }
        await ctx.send()
        (list, running_count) = await getTask(ctx)
        body = {
            "list": list,
            "running_count": running_count
        }
        await ctx.serve.push(InfoType.SUCCESS, "task-list/update", body)
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()

@server.registerHandle("/task/edit")
async def editTask(ctx: Ctx):
    try:
        id = await ctx.serve.task.update_task(ctx.data)
        await ctx.serve.task.update_task_status(ctx.data["id"], 1)
        ctx.status = Status.OK
        ctx.body = {
            "id": id
        }
        await ctx.send()
        (list, running_count) = await getTask(ctx)
        body = {
            "list": list,
            "running_count": running_count
        }
        await ctx.serve.push(InfoType.SUCCESS, "task-list/update", body)
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()

@server.registerHandle("/task/update")
async def updateTaskStatus(ctx: Ctx):
    try:
        task = await ctx.serve.task.get_task_by_id(ctx.data["id"])
        taskBody = {
            "id": task[0],
            "name": task[1],
            "type": task[2],
            "status": task[3],
            "time": task[4],
            "content": task[5],
            "member": task[6].split(","),
        }
        # 如果 状态修改为进行中，那么就要把任务添加到定时任务中
        if (ctx.data["status"] == 2):
            ## 获取任务信息
            ctx.serve.registerTime.add(taskBody)
        # 如果 状态修改为未开始，那么就要把任务从定时任务中移除
        elif (ctx.data["status"] == 1):
            ctx.serve.registerTime.remove(taskBody)
        # 如果取消任务，那么就要把任务从定时任务中移除
        elif (ctx.data["status"] == 4):
            ctx.serve.registerTime.remove(taskBody)
            # 遍历任务队列，如果有任务id相同的，那么就移除
            def removeTask():
                new_queue = queue.Queue()
                while not task_queue.empty():
                    task = task_queue.get()
                    if task.get("id") == ctx.data["id"]:
                        task_queue.task_done()
                    else:
                        new_queue.put(task)
                
                # 将剩余的任务重新放回任务队列
                while not new_queue.empty():
                    task_queue.put(new_queue.get())
            removeTask()
            
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()
    
    try: 
        await ctx.serve.task.update_task_status(ctx.data["id"], ctx.data["status"])
        ctx.status = Status.OK
        ctx.body = {
            "id": ctx.data["id"]
        }
        await ctx.send()
        (list, running_count) = await getTask(ctx)
        body = {
            "list": list,
            "running_count": running_count
        }
        await ctx.serve.push(InfoType.SUCCESS, "task-list/update", body)
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()
