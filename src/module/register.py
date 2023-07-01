import asyncio
import os
import ssl
import aiomysql

from dotenv import load_dotenv

from src.globals import get_loop


ssl_ctx = os.getenv("MYSQL_SSL")

if ssl_ctx == "True":
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.load_default_certs()
else:
    ssl_ctx = None

load_dotenv()

async def register():
    '''
    初始化，获取数据库连接池
    :return:
    '''
    loop = get_loop()
    try:
        print("start to connect db!")
        POOL = await aiomysql.create_pool(
            host=os.getenv("MYSQL_HOST"),
            port=3306,
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE"),
            charset='utf8',
            loop=loop,
            ssl=ssl_ctx,
        )
        return POOL
    except asyncio.CancelledError:
        raise asyncio.CancelledError
    except Exception as ex:
        print(ex)
        return False