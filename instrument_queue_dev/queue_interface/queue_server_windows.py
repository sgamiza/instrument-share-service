#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import queue
import logging
import threading
from multiprocessing.managers import BaseManager

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import sys
# sys.path.append("..")

from instrument_queue_dev.queue_handler.queue_handler_manager import QueueHandlerManager


logger = logging.getLogger(__name__)



logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s %(asctime)s %(filename)s %(funcName)s %(lineno)s - %(message)s")

STATUS_OK = {"STATUS": "OK"}
STATUS_ERR = {"STATUS": "ERROR"}



# 发送任务的队列:
lock_queue = queue.Queue()
# 接收结果的队列:
# result_queue = queue.Queue()


# 【windows】
# 增加如下的函数以适应windows ,【PicklingError】
def queue_callable():
    return lock_queue


# def result_queue_fun():
#     return result_queue
#     # return queue.Queue()  # 这样不行


# 从BaseManager继承的QueueManager:
class QueueManager(BaseManager):
    instance = None


class NewSingleQueue(type):
    _lock = threading.Lock()

    def __call__(cls, address, authkey, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with NewSingleQueue._lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(NewSingleQueue, cls).__call__(address, authkey, *args, **kwargs)  # 1. 这里要全
                    
        # robot 运行的时候需要删除，不然报错找不到shutdown属性错误
        else:
            with NewSingleQueue._lock:
                cls._instance.shutdown()
                cls._instance = super(NewSingleQueue, cls).__call__(address, authkey, *args, **kwargs)
        # print(cls._instance)
        return cls._instance  # 需要return



class InstrumentQueueManager(BaseManager, metaclass=NewSingleQueue):

    def __new__(cls, address, authkey, **kwargs):
        return super().__new__(cls, **kwargs)  # 3. __new__需要return

    def __init__(self, address, authkey, *args, **kwargs):
        super().__init__(address, authkey, *args, **kwargs)  # 不要忘记（*args, **kwargs），不然client连接错误
        # Tobe Done

    @classmethod
    def created(cls):
        return hasattr(cls, "_instance")


def create_queue(queue_name, callback, queue_address='127.0.0.1', auth=b'YOUR_AUTHKEY'):
    queue_address_port = (queue_address, 5000)
    queue_manager = InstrumentQueueManager(address=queue_address_port, authkey=auth)
    queue_manager.register(queue_name, callable=callback)
    queue_manager.start()
    return queue_manager, getattr(queue_manager, queue_name)()


def request_dispatch_by_instrument_id(queue_handler_api, request, blocker_ip="localhost"):
    # TODO 错误处理，instrument_id不存在等
    instrument_id = request["instrument_id"]
    logger.info('Job will be dispatched to instrument with ID: %s' % instrument_id)
    # server注册instrument
    queue_handler_api.attach(instrument_id=instrument_id, blocker_ip=blocker_ip)
    # 任务分发
    queue_handler_api.dispatch_queue(request, instrument_id=instrument_id)


# TODO 删除main
if __name__ == '__main__':

    blocker_ip = "localhost"

    # 创建 task_lock_request 监听任务
    # windows
    qm, q_task_lock_request = create_queue("task_lock_request", queue_callable, queue_address=blocker_ip)
    count = 0
    api = QueueHandlerManager()

    while True:
        # instrument_ip = "default ip"
        count += 1
        print(str(count) + "*" * 100)
        result_playload = {}
        instrument_hold_time = 0
        # res = None
        # 从task_lock_request队列读取请求
        r = q_task_lock_request.get()

        # print(type(r))  # JSONObject()
        # print(r)  # JSONObject()
        # print(q_task_lock_request.__dict__['_token'].typeid)  # task_lock_request 队列名称

        # TODO 添加新的分布式任务队列
        # qm_new, q_new = create_queue(instrument_ip, queue_callable)
        # q_task_lock_request = getattr(qm_new, "task_lock_request")()  # 用qm会报 server not yet started 错误
        # new queue add notify
        # publish.single(topic="create_queue/test", payload="new queue", hostname=host)
        # print("MQTT: create_queue done !")

        # 单队列实现
        # from instrument_queue_dev.queue_handler.queue_handler import QueueHandler
        # queue_handler = QueueHandler("instrument_id", mqtt_blocker_ip="localhost")
        # queue_handler.dispatch(r)
        # 多队列实现
        request_dispatch_by_instrument_id(api, r, blocker_ip=blocker_ip)

