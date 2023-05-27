import asyncio
import time
import pyautogui as pg
import pyperclip as pc
from globals import InfoType, get_loop, task_queue
from info_queue import push

open_wchat = ["ctrl", "alt", "w"]
wchat_search = ["ctrl", "f"]
PAUSE = 1.5

def report(task):
    loop = get_loop()
    future = asyncio.run_coroutine_threadsafe(task, loop)
    return future.result()

def worker():
    while True:
        task = task_queue.get()
        consumption(task)
        task_queue.task_done()
    
def consumption(task):
    try:
        push(InfoType.Success, "start task: {}".format(task.get("name")))
        # send_wx_message(task)
        time.sleep(2)
        push(InfoType.Success, "run task {} success".format(task.get("name")))
    except Exception as e:
        push(InfoType.ERROR, "error: {}".format(e))

def send_wx_message(task):
    """
    定时发送信息给微信联系人
    """
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

