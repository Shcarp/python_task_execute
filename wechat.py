from service.wrap_pb import Status, InfoType
from globals import server
from service.websocket import Ctx

async def getList(ctx: Ctx):
    data = await ctx.serve.wechat.get_wechat_name_list()

    dataList = list(data)

    res = []
    # 遍历dataList 取出每一个元素
    for item in dataList:
        res.append(item[1])
    return res

@server.registerHandle("/wxuser/add")
async def addWxName(ctx: Ctx):
    try:
        id = await ctx.serve.wechat.create_wechat_name(ctx.data["wx_name"])
        ctx.status = Status.OK
        ctx.body = {
            "id": id
        }
        await ctx.send()
        await ctx.serve.push(InfoType.SUCCESS, "wechat-name/add", await getList(ctx))

    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()

@server.registerHandle("/wxuser/list")
async def getWxNameList(ctx: Ctx):
    try:
        ctx.status = Status.OK
        ctx.body = await getList(ctx)
        await ctx.send()
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()
    
