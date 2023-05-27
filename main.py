import os
import sys
import time
import threading
import schedule
from register_time import RegisterTime
from run_task import worker
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
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("exit")
            break
        except Exception as e:
            # handle the exception here
            print("Error: {}".format(e))
            # restart the program
            os.execv(__file__, sys.argv)
