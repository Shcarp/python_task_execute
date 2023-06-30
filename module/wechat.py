

from module.mysql import TransactionDecorator

class WechatNamesMySql:
    pool = None
    def __init__(self, pool) -> None:
        self.pool = pool

    async def getCursor(self):
        '''
            获取db连接和cursor对象，用于db的读写操作
            :param pool:
            :return:
        '''
        conn = await self.pool.acquire()
        cur = await conn.cursor()
        return conn, cur
    
    @TransactionDecorator
    async def init_sql(self, cursor, init_func):
        # 判断任务表是否存在，不存在则创建
        await cursor.execute("SHOW TABLES LIKE 'wechat_names'")
        if (cursor.fetchone().result() is None):
            await cursor.execute("CREATE TABLE wechat_names (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(100) NOT NULL)")
        if init_func is not None:
            await init_func(self)

    @TransactionDecorator
    async def create_wechat_name(self, cursor, name):
        # 在微信昵称表中插入新昵称
        query = "INSERT INTO wechat_names (name) VALUES (%s)"
        await cursor.execute(query, (name,))
        # 获取新插入昵称的ID
        name_id = cursor.lastrowid
        return name_id
    
    # 获取微信昵称列表
    @TransactionDecorator
    async def get_wechat_name_list(self, cursor):
        query = "SELECT * FROM wechat_names"
        await cursor.execute(query)
        name_list = cursor.fetchall()
        return name_list.result()

