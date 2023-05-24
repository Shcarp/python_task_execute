
async def getList(ctx):
    data = await ctx.serve.wechat.get_wechat_name_list()

    dataList = list(data)

    res = []
    # 遍历dataList 取出每一个元素
    for item in dataList:
        res.append(item[1])
    return res

async def addWxName(ctx):
    print("addWxName")
    try:
        id = await ctx.serve.wechat.create_wechat_name(ctx.data["wx_name"])
        ctx.status = 200
        ctx.body = {
            "id": id
        }
        await ctx.send()
        await ctx.serve.push({
            "event": "wechat-name/add",
            "data": await getList(ctx)
        })
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()

async def getWxNameList(ctx):
    try:
        ctx.status = 200
        ctx.body = await getList(ctx)
        await ctx.send()
    except Exception as e:
        ctx.status = 500
        ctx.body = "error: {}".format(e)
        await ctx.send()
    
