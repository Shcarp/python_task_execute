import os
import sys
import multiprocessing
from src.main import main
from src.lock import acquire_lock, release_lock

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
            if os.path.exists(os.path.join(os.getcwd(), "message.lock")):
                release_lock()



