import compileall
import os

compileall.compile_file(os.path.join(os.getcwd(), 'cache', 'testbytes', 'testbytes.py'), force=True)