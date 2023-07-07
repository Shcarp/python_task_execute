# 创建虚拟运行环境
# python3 -m venv venv
#
import json
import os
from asyncio import subprocess
import re
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
        # 保存真正执行的进程，用于关闭，有多个
        self.process = []

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
    
    def stop(self):
        for process in self.process:
            process.terminate()
            # 从列表中移除
            self.process.remove(process)

    def getPython(self):
        if self.v_python is None:
            self.v_python = self.create(path=self.path)
        return self.v_python
    
    # 安装包
    async def install(self, package):
        venv_python = self.getPython()
        await subprocess.create_subprocess_exec(venv_python, "-m", "pip", "install",  package)

    # 移除包
    async def uninstall(self, package):
        venv_python = self.getPython()
        await subprocess.create_subprocess_exec(venv_python, "-m", "pip", "uninstall", "-y", package)

    # 执行
    async def execute(self, code, params: Params, ):
        # 将参数序列化为json字符串
        p_str = params.toJSON()
        venv_python = self.getPython()
        process = await subprocess.create_subprocess_exec(venv_python, "-c", code, p_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.process.append(process)
        stdout, stderr = await process.communicate()
        # 从列表中移除
        self.process.remove(process)
        

        if(stderr.decode() != ""):
            raise Exception(stderr.decode())
        
        # 从stdout中获取返回值

        all_out = stdout.decode()
        # run 的返回值使用json字符串,res是字符串，需要提取RUN^^^^RES中内容
        result = re.search(r"RUN\^\^(.*)\^\^RES", all_out, re.S)

        if result is None:
            res = None
        else:
            res = result.group(1)
        return res
    