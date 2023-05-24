import time
import threading
import schedule
import globals
from register_time import RegisterTime
from runTask import worker
from server import run_server

def main():
    register = RegisterTime()

    server_thread = threading.Thread(target=run_server, args=(register,))
    server_thread.start()

    task_run_thread = threading.Thread(target=worker)
    task_run_thread.start()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
