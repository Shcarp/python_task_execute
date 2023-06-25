import multiprocessing
import os
import sys
import time
import threading
import schedule
from mtime.register_time import RegisterTime
from run_task import worker
from server import run_server

LOCK_NAME= "message.lock"

def acquire_lock():
    path = os.path.join(os.getcwd(), LOCK_NAME)
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


def main():
    register = RegisterTime()

    # 启动websocket服务
    server_thread = threading.Thread(target=run_server, args=(register,))
    server_thread.start()

    # 启动任务线程，从task_queue中获取任务
    task_run_thread = threading.Thread(target=worker)
    task_run_thread.start()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    acquire_lock()
    while True:
        try:
            p = multiprocessing.Process(target=main)
            p.daemon = True
            p.start()
            p.join()
        except KeyboardInterrupt:
            print("exit")
            break
        except Exception as e:
            # handle the exception here
            print("Error: {}".format(e))
            # restart the program
            os.execv(__file__, sys.argv)
        finally:
            release_lock()
