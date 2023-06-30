
from abc import ABC, abstractmethod

class PythonRunner(ABC):
    @staticmethod
    def register(execute_name):
        def wrapper(cls):
            PythonRunner.dir[execute_name] = cls
            return cls
        return wrapper

    @staticmethod
    def getInstance(kind, path) -> 'PythonRunner':
        return PythonRunner.dir[kind](path)
    
    def __init__(self, path) -> None:
       self.path = path

    @abstractmethod
    def run(self):
        pass

@PythonRunner.register("py")
class PythonSourceCodeRunner(PythonRunner):
    def __init__(self, path):
        super().__init__(path)

    def run(self):
        pass

@PythonRunner.register("pyc")
class PythonByteCodeRunner(PythonRunner):
    def __init__(self, path):
        super().__init__(path)

    def run(self):
        pass

@PythonRunner.register("package")
class PythonPackageRunner(PythonRunner):
    def __init__(self, path):
        super().__init__(path)

    def run(self):
        pass
