from globals import server
from service.transport import Ctx
from service.wrap_pb import Status

@server.registerHandle("test")
async def getWxNameList(ctx: Ctx):
    print("test", ctx.data)
    try:
        ctx.status = Status.OK
        ctx.body = 2
        await ctx.send()
    except Exception as e:
        ctx.status = Status.INTERNAL_SERVER_ERROR
        ctx.body = "error: {}".format(e)
        await ctx.send()
    