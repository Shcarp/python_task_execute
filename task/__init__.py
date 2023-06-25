
class ExecuteTaskConfig:
    name: str = None
    location: str = None
    path: str = None
    params: dict = None
    def __init__(self, name, location, path, params):
        self.name = name
        self.location = location
        self.path = path
        self.params = params

class TaskConfig:
    id: int = 0
    name: str = None
    # 脚本位置
    location: str = None
    # 脚本路径
    path: str = None
    # 任务参数
    params: dict = None
    # 任务状态
    status: int = 0
    # 执行次数
    execute_count: int = 0
    # 脚本类型 阻塞的，不阻塞的
    # 如果是阻塞的，那么就放入task队列中，等待执行
    # 如果是不阻塞的，那么开起一个新的线程去执行
    execute_type: str = None
    # 执行结果
    execute_result: list = None
    # 执行时间类型，有定时执行，和固定时间执行
    execute_time_type: str = None
    # 执行时间
    execute_time: str = None

    def __init__(self, 
                 id, 
                 name, 
                 location, 
                 path,
                 params, 
                 status, 
                 execute_count, 
                 execute_type, 
                 execute_result, 
                 execute_time_type, 
                 execute_time
                 ):
        self.id = id
        self.name = name
        self.location = location
        self.path = path
        self.params = params
        self.status = status
        self.execute_count = execute_count
        self.execute_type = execute_type
        self.execute_result = execute_result
        self.execute_time_type = execute_time_type
        self.execute_time = execute_time
