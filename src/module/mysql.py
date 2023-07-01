
# Desc: mysql操作
from abc import ABC

class TransactionDecorator:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self.func
        return self._wrapper(instance)

    def _wrapper(self, instance):
        async def wrapped(*args, **kwargs):
            conn, cur = await instance.getCursor()
            try:
                result = await self.func(instance, cur, *args, **kwargs)
                await conn.commit()
                return result
            except Exception as e:
                await conn.rollback()
                raise e
            finally:
                await instance.pool.release(conn)
        return wrapped

class MysqlConnect(ABC):
    def __init__(self, pool) -> None:
        self.pool = pool

    async def getCursor(self):
        '''
            获取db连接和cursor对象,用于db的读写操作
            :param pool
            :return
        '''
        conn = await self.pool.acquire()
        cur = await conn.cursor()
        return conn, cur
