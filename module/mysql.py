
# Desc: mysql操作
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
