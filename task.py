from globals import task_queue
keyword = ""

async def getTask(ctx):
    global keyword
    if ( "keyword" in ctx.data):
        keyword = ctx.data["keyword"]

    list = await ctx.serve.task.get_task_list({
            "keyword": keyword
        })

    res = []
    for item in list:
        res.append({
            "id": item[0],
            "name": item[1],
            "type": item[2],
            "status": item[3],
            "time": item[4],
            "content": item[5],
            "member": item[6].split(",")
        })
    return res

async def getTaskList(ctx):
    try:
        ctx.status = 200
        ctx.body = await getTask(ctx)
        await ctx.send()
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()

async def addTask(ctx):
    try:
        insertdata = ctx.data
        insertdata["status"] = "nostarted"
        id = await ctx.serve.task.create_task(insertdata)
        ctx.status = 200
        ctx.body = {
            "id": id
        }
        await ctx.send()
        await ctx.serve.push({
            "event": "task-list/update",
            "data": await getTask(ctx)
        })
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()

async def editTask(ctx):
    try:
        id = await ctx.serve.task.update_task(ctx.data)
        ctx.serve.task.update_task_status(ctx.data["id"], "nostarted")
        ctx.status = 200
        ctx.body = {
            "id": id
        }
        await ctx.send()
        await ctx.serve.push({
            "event": "task-list/update",
            "data": await getTask(ctx)
        })
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()



async def updateTaskStatus(ctx):

    async def callback(event, message):
        await ctx.serve.push({
            "event": event,
            "data": message
        })

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
            "callback": callback
        }
        # 如果 状态修改为进行中，那么就要把任务添加到定时任务中
        if (ctx.data["status"] == "progress"):
            ## 获取任务信息
            ctx.serve.registerTime.add(taskBody)
        # 如果 状态修改为未开始，那么就要把任务从定时任务中移除
        elif (ctx.data["status"] == "nostarted"):
            ctx.serve.registerTime.remove(taskBody)
        # 如果取消任务，那么就要把任务从定时任务中移除
        elif (ctx.data["status"] == "cancel"):
            global task_queue
            ctx.serve.registerTime.remove(taskBody)
            # 遍历任务队列，如果有任务id相同的，那么就移除
            for item in task_queue:
                if (item["id"] == ctx.data["id"]):
                    task_queue.remove(item)

            
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()
    
    try: 
        await ctx.serve.task.update_task_status(ctx.data["id"], ctx.data["status"])
        ctx.status = 200
        ctx.body = {
            "id": ctx.data["id"]
        }
        await ctx.send()
        await ctx.serve.push({
            "event": "task-list/update",
            "data": await getTask(ctx)
        })
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()

    
