import os
import tarfile
import toml
import zipfile
from abc import ABC, abstractmethod

from isolate import Isolate, Params

params_code = '''
class Params:
    file_path = None
    params = None
    def __init__(self, file_path, params) -> None:
        self.file_path = file_path
        self.params = params

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def parseJSON(json_str):
        params = json.loads(json_str)
        return Params(params["file_path"], params["params"])
'''

class PythonRunner(ABC):
    DIR = {}
    path: str = None
    packages: list = []
    isolate = None

    @staticmethod
    def register(execute_name):
        def wrapper(cls):
            PythonRunner.DIR[execute_name] = cls
            return cls
        return wrapper

    @staticmethod
    def getInstance(kind, path) -> 'PythonRunner':
        return PythonRunner.DIR[kind](path)
    
    def __init__(self, path) -> None:
       self.packages = []
       self.isolate = Isolate(os.path.join(os.path.dirname(__file__), 'ISOLATE'))
       self.path = path
       self.check()

    def check(self):
        self.doCheck()

    @abstractmethod
    def doCheck(self):
        pass
    
    @abstractmethod
    def run(self, params=None):
        pass

    def remove(self):
        for i in self.packages:
            self.isolate.uninstall(i)

@PythonRunner.register("py")
class PythonSourceCodeRunner(PythonRunner):
    source_code: str = None
    config: dict = None
    def __init__(self, path):
        super().__init__(path)
        packages = self.config.get('package')
        for package in packages:
            version = packages[package]
            p = package + ('==' + version) if version != '0.0.0' else package
            self.isolate.install(p)
            self.packages.append(p)

    def wrap(self, code):
        return f'''
import sys
import json
import os
import argparse
{code}
{params_code}
def main(params: Params):
    run(params.params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('params', help='params')
    args = parser.parse_args()
    main(Params.parseJSON(args.params))
'''

    def doCheck(self):
        zip_file = zipfile.ZipFile(self.path)
        script_file = zip_file.namelist()

        def filePath(path):
            path = self.path.split('/')[-1].split('.')[0] + '/' + path
            return path
        
        config = False
        main = False
        for file in script_file:
            if file == filePath('main.py'):
                main = True
            if file == filePath('config.toml'):
                config = True
        if(not config):
            raise Exception("config.toml not found")
        if(not main):
            raise Exception("main.py not found")

        self.config = toml.loads(zip_file.read(filePath('config.toml')).decode('utf-8'))
        self.source_code = zip_file.read(filePath('main.py')).decode('utf-8')
        
    def run(self, params=None):
        params = Params(os.path.join(os.getcwd(), "cache", "test.pyc"), params= params)

        try:
            self.isolate.execute(self.wrap(self.source_code), params=params)
            print("running python source code")
        except Exception as e:
            raise Exception("running python source code error: " + str(e))
        

@PythonRunner.register("pyc")
class PythonByteCodeRunner(PythonRunner):
    bytes_code: bytes = None

    def __init__(self, path):
        super().__init__(path)
        packages = self.config.get('package')

        for package in packages:
            version = packages[package]
            p = package + ('==' + version) if version != '0.0.0' else package
            self.isolate.install(p)
            self.packages.append(p)

    def wrap(self):
        return f'''
import sys
import json
import os
import argparse
import tempfile
import importlib

{params_code}

bytes_code = {self.bytes_code}

f = tempfile.NamedTemporaryFile(suffix='.pyc', delete=False)
f.write(bytes_code)
f.close()

module_name = "example"
spec = importlib.util.spec_from_file_location(module_name, f.name)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def main(params: Params):
    module.run(params.params)
    # 清除临时文件
    os.remove(f.name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('params', help='params')
    args = parser.parse_args()
    main(Params.parseJSON(args.params))
'''

    def doCheck(self):
        zip_file = zipfile.ZipFile(self.path)
        script_file = zip_file.namelist()

        def filePath(path):
            path = self.path.split('/')[-1].split('.')[0] + '/' + path
            return path
        
        config = False
        main = False
        for file in script_file:
            if file == filePath('main.pyc'):
                main = True
            if file == filePath('config.toml'):
                config = True
        if(not config):
            raise Exception("config.toml not found")
        if(not main):
            raise Exception("main.pyc not found")

        self.config = toml.loads(zip_file.read(filePath('config.toml')).decode('utf-8'))
        self.bytes_code = zip_file.read(filePath('main.pyc'))

    def run(self, params=None):

        params = Params(os.path.join(os.getcwd(), "cache", "test.pyc"), params= params)

        try:
            self.isolate.execute(self.wrap(), params=params)
            print("running python byte code")
        except Exception as e:
            raise Exception("running python byte code error: " + str(e))

@PythonRunner.register("package")
class PythonPackageRunner(PythonRunner):
    package_name: str = None
    def __init__(self, path):
        super().__init__(path)
        # 安装包
        self.isolate.install(self.path)
        self.package_name = self.packages[0]

    def wrap(self):
        return f'''
import sys
import json
import os
import argparse
import {self.package_name}

{params_code}

def main(params: Params):
    {self.package_name}.run(params.params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('params', help='params')
    args = parser.parse_args()
    main(Params.parseJSON(args.params))
'''

    def doCheck(self):
        # 在window 环境
        if os.name == 'nt':
            # zip 文件
            if self.path.endswith('.zip'):
                def filePath(path):
                    path = self.path.split('/')[-1].split('.')[0] + '/' + path
                    return path
                with zipfile.ZipFile(self.path, 'r') as zip_ref:
                    if filePath('METADATA') in zip_ref.namelist():
                        metadata_file = zip_ref.open(filePath('METADATA'))
                    elif filePath('PKG-INFO') in zip_ref.namelist():
                        metadata_file = zip_ref.open(filePath('PKG-INFO'))
                    else:
                        raise ValueError("未找到元数据文件")
                    
                    for line in metadata_file:
                        line = line.decode('utf-8')
                        if line.startswith('Name:'):
                            self.packages.append(line.split(':', 1)[1].strip())
                            return
                    
                    raise ValueError("无法获取包名称")
        # 在mac 环境
        elif os.name == 'posix':
            # tar.gz 文件
            if self.path.endswith('.tar.gz'):
                # 从ddNum-0.0.1.tar.gz 中获取 ddNum-0.0.1
                with tarfile.open(self.path, 'r:gz') as tar_ref:
                    def filePath(path):
                        path = self.path.split('/')[-1][:-7] + '/' + path
                        return path
                    if filePath('PKG-INFO') in tar_ref.getnames():
                        metadata_file = tar_ref.extractfile(filePath('PKG-INFO'))
                    elif filePath('METADATA') in tar_ref.getnames():
                        metadata_file = tar_ref.extractfile(filePath('METADATA'))
                    else:
                        raise ValueError("未找到元数据文件")
                    
                    for line in metadata_file:
                        line = line.decode('utf-8')
                        if line.startswith('Name:'):
                            self.packages.append(line.split(':', 1)[1].strip())
                            return 

                    raise ValueError("无法获取包名称")       

    def run(self, params=None):
        params = Params(os.path.join(os.getcwd(), "cache", "test.pyc"), params= params)
        try:
            self.isolate.execute(self.wrap(), params=params)
        except Exception as e:
            raise Exception("running python package error: " + str(e))


def testSourceCode():
    path = os.path.join(os.path.dirname(__file__), "../" ,"__test__/test.zip")
    runner = PythonRunner.getInstance("py", path=path)
    runner.run({"a": 1, "b": 2})

def testBytesCode():
    path = os.path.join(os.path.dirname(__file__), "../" ,"__test__/testbytes.zip")
    runner = PythonRunner.getInstance("pyc", path=path)
    runner.run({"a": 1, "b": 2})

def testPackage():
    path = os.path.join(os.path.dirname(__file__), "../" ,"__test__/addNum-0.0.1.tar.gz")
    runner = PythonRunner.getInstance("package", path=path)
    runner.run({"a": 1, "b": 2})

# testSourceCode()
# testBytesCode()
# testPackage()