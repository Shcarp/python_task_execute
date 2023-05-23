import asyncio
import queue
import time
import pyautogui as pg
import pyperclip as pc

from loop import get_loop

open_wchat = ["ctrl", "alt", "w"]
wchat_search = ["ctrl", "f"]
PAUSE = 1.5

task_queue = queue.Queue()

def push(task):
    task_queue.put_nowait(task)

async def init_task(server, regsitertime, task_module):
    task_list = await task_module.get_all_status_task("progress")
    async def callback(event, message):
        await server.push({
            "event": event,
            "data": message
        })

    for item in task_list:
        regsitertime.add({
            "id": item[0],
            "name": item[1],
            "type": item[2],
            "time": item[4],
            "content": item[5],
            "member": item[6].split(","),
            "callback": callback
        })

def run_in_loop(task):
    loop = get_loop()
    future = asyncio.run_coroutine_threadsafe(task, loop)
    return future.result()

def worker():
    while True:
        task =  task_queue.get()
        print("task: ", task["name"])
        consumption(task)
        task_queue.task_done()
    
def consumption(task):
    run_in_loop(task["callback"]("execute-info", "start"))
    send_wx_message(task)

def send_wx_message(task):
    """
    定时发送信息给微信联系人
    """
    try:
        content = task.get("content")
        # 这里是微信联系人名字，或者群名称都可以
        # 操作间隔为1秒
        pg.PAUSE = PAUSE
        # 快捷键调出桌面微信客户端
        pg.hotkey(*open_wchat)
        # 找到好友
        for dex in task.get("member"):
            # 打开搜索框
            pg.hotkey(*wchat_search)
            # 输入名字
            pc.copy(dex)
            # 粘贴
            pg.hotkey('ctrl', 'v')
            # 回车
            pg.press('enter')

            # 发送消息
            pc.copy(content)
            pg.hotkey('ctrl', 'v')
            pg.press('enter')

        # 隐藏微信
        time.sleep(1)
        pg.hotkey(*open_wchat)

        run_in_loop(task["callback"]("execute-info", "success"))
    except Exception as e:
        run_in_loop(task["callback"]("execute-error", "error: {}".format(e)))

