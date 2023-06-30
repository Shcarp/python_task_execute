
import os

from isolate import Isolate, Params

isolate = Isolate(os.path.join(os.getcwd(), "ISOLATE"))

isolate.install("importlib")
isolate.install("websocket")

params = Params(os.path.join(os.getcwd(), "cache", "test.pyc"), {"a": 1, "b": 2})

isolate.execute(params=params)
