import os
import sys

LOCK_NAME= "message.lock"

def acquire_lock():
    path = os.path.join(os.getcwd(), LOCK_NAME)
    print(path)
    # 判断文件是否存在, 存在则退出，不存在则创建, 并加锁
    if os.path.exists(path):
        print("The file is exists, exit")
        sys.exit(0)
    else:
        # 创建文件
        open(path, "w").close()

def release_lock():
    path = os.path.join(os.getcwd(), LOCK_NAME)
    # 删除文件
    os.remove(path)
