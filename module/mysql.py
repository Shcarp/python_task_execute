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
            conn, cur = await instance.getCurosr()
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

class TaskMySql:
    pool = None
    def __init__(self, pool) -> None:
        self.pool = pool

    async def getCurosr(self):
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
        await cursor.execute("SHOW TABLES LIKE 'task'")
        if (cursor.fetchone().result() is None):
            await cursor.execute("CREATE TABLE task ( id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,type VARCHAR(50),status VARCHAR(50),time BIGINT,content TEXT,member VARCHAR(200))")
        if init_func is not None:
            await init_func(self)

    @TransactionDecorator
    async def create_task(slef, cursor, task_data):
        # 在任务表中插入新任务的数据
        query = "INSERT INTO task (name, type, status, time, content, member) VALUES (%s, %s, %s, %s, %s, %s)"
        await cursor.execute(query, (task_data['name'], task_data['type'], task_data['status'], task_data['time'], task_data['content'], ",".join(task_data['member'])))
        # 获取新插入任务的ID
        task_id = cursor.lastrowid
        return task_id
    
    # 获取任务列表
    @TransactionDecorator
    async def get_task_list(self, cursor, data):
        query = "select * from task where name like '%"+data["keyword"]+"%' order by id desc"
        await cursor.execute(query)
        task_list = cursor.fetchall()
        return task_list.result()
    
    # 更新任务信息
    @TransactionDecorator
    async def update_task(self, cursor, task_data):
        query = "UPDATE task SET name = %s, type = %s, status = %s, time = %s, content = %s, member = %s WHERE id = %s"
        await cursor.execute(query, (task_data['name'], task_data['type'], task_data['status'], task_data['time'], task_data['content'], ",".join(task_data['member']), task_data['id']))
        return task_data['id']

    # 更新任务状态
    @TransactionDecorator
    async def update_task_status(self, cursor, task_id, status):
        query = "UPDATE task SET status = %s WHERE id = %s"
        await cursor.execute(query, (status, task_id))
        return task_id
    
    # 获取所有进行中的任务
    @TransactionDecorator
    async def get_all_status_task(self, cursor, status):
        query = "SELECT * FROM task WHERE status = %s"
        await cursor.execute(query, (status,))
        task_list = cursor.fetchall()
        return task_list.result()

    # 根据ID获取任务
    @TransactionDecorator
    async def get_task_by_id(self, cursor, task_id):
        query = "SELECT * FROM task WHERE id = %s"
        await cursor.execute(query, (task_id,))
        task = cursor.fetchone()
        return task.result()


class WechatNamesMySql:
    pool = None
    def __init__(self, pool) -> None:
        self.pool = pool

    async def getCurosr(self):
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
            print("create wechat_names")
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
