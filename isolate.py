# 创建虚拟运行环境
# python3 -m venv venv
#
import json
import os
import subprocess
from venv import EnvBuilder

wrap_python_code = '''
import sys
import json
import os
import argparse
from importlib.util import module_from_spec, spec_from_file_location

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

def run(params: Params):
    path = params.file_path
    params = params.params
    module_name = os.path.basename(path).split(".")[0]
    spec = spec_from_file_location(module_name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.run()
    print(path)
    print(params)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('params', help='params')
    args = parser.parse_args()
    run(Params.parseJSON(args.params))
'''

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
        return json.loads(json_str)

class Isolate:
    path = os.path.join(os.getcwd(), "ISOLATE")
    v_python = None
    def __init__(self, path) -> None:
        self.path = path
        # 判断是否存在虚拟环境
        if os.path.exists(path):
            return
        else:
            # 创建虚拟环境
            self.create(path)

    def create(self, path):
        builder = EnvBuilder(
            system_site_packages=True,
            clear=False,
            symlinks=False,
            upgrade=True,
            with_pip=True,
            prompt=None,
        )
        builder.create(path)
        venv_python = os.path.join(path, "bin", "python")
        return venv_python

    def getPython(self):
        if self.v_python is None:
            self.v_python = self.create(path=self.path)
        return self.v_python
    
    # 安装包
    def install(self, package):
        venv_python = self.getPython()
        subprocess.check_call([venv_python, "-m", "pip", "install", package])

    # 移除包
    def uninstall(self, package):
        venv_python = self.getPython()
        process = subprocess.check_call([venv_python, "-m", "pip", "uninstall", package])
        process.wait()

    # 执行
    def execute(self, params: Params):
        # 将参数序列化为json字符串
        p_str = params.toJSON()
        venv_python = self.getPython()
        process = subprocess.Popen([venv_python, "-c", wrap_python_code, p_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if(stderr.decode() != ""):
            print(stderr.decode())
            raise Exception(stderr.decode())
        print(stdout.decode())
        return stdout.decode()
    