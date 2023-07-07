# 创建虚拟运行环境
# python3 -m venv venv
#
import json
import os
from asyncio import subprocess
# import subprocess
import sys
from venv import EnvBuilder

number = 0

class Params:
    def __init__(self, file_path, params) -> None:
        self.file_path = file_path
        self.params = params

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def parseJSON(json_str):
        return json.loads(json_str)

class PythonIsolate:
    def __init__(self, path) -> None:
        self.v_python = None
        self.path = path
        # 判断是否存在虚拟环境
        if os.path.exists(self.path):
            self.v_python = os.path.join(self.path, "bin", "python")
        else:
            # 创建虚拟环境
            self.v_python = self.create(self.path)

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
    async def install(self, package):
        venv_python = self.getPython()
        await subprocess.create_subprocess_exec(venv_python, "-m", "pip", "install",  package)
        # subprocess.check_call([venv_python, "-m", "pip", "install",  package])

    # 移除包
    async def uninstall(self, package):
        venv_python = self.getPython()
        # subprocess.check_call([venv_python, "-m", "pip", "uninstall", "-y", package])
        await subprocess.create_subprocess_exec(venv_python, "-m", "pip", "uninstall", "-y", package)

    # 执行
    async def execute(self, code, params: Params):
        # 将参数序列化为json字符串
        p_str = params.toJSON()
        venv_python = self.getPython()
        # process = subprocess.Popen([venv_python, "-c", code, p_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process = await subprocess.create_subprocess_exec(venv_python, "-c", code, p_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if(stderr.decode() != ""):
            raise Exception(stderr.decode())
        return stdout.decode()
        # subprocess.check_call([venv_python, "-c", code, p_str])
    