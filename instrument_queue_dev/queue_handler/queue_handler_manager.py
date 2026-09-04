
import logging
import json

from instrument_queue_dev.storage.stores_interface import JSONObject
from instrument_queue_dev.optional_lab import LookupHandler, exceptions
from instrument_queue_dev.queue_handler.base_handler import BaseHandler
from .queue_handler import QueueHandler


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class QueueHandlerManager(BaseHandler):
    # 子类使用方法
    # lookup_handler = LookupHandler("connection", QueueHandler)
    lookup_handler = LookupHandler("handler", QueueHandler)

    def __init__(self):
        self.lookup_handler.store = self.store

    # 加入【对象】和【别名】对应关系
    def attach(self, instrument_id, blocker_ip="localhost"):

        try:
            return self.store.get(instrument_id)
        except exceptions.AliasLookupError:
            handler = QueueHandler(instrument_id, mqtt_blocker_ip=blocker_ip)
            self.store.add(handler, instrument_id)
            return handler


    # 该装饰器函数不调用也会执行，instrument_id 参数不存在会报下面的错：
    # TypeError: no 'instrument_id' argument found in 'dispatch_queue' signature.
    # @lookup_handler.implicit_lookup
    # def test(self, timeout=10, handler=None):
    #     pass

    @lookup_handler.implicit_lookup
    def get_handler_object(self, handler=None):
        print("handler_object: ", handler)


    # 父类函数功能更加强大
    # @lookup_handler.implicit_lookup
    # def dispatch_queue(self, task_lock_request, handler=None):
    #     handler.dispatch(task_lock_request)



# TODO 删除 __main__
if __name__ == '__main__':
    api = QueueHandlerManager()

    conn1 = api.attach(instrument_id="id1", blocker_ip="localhost")
    api.attach(instrument_id="id2", blocker_ip="localhost")
    # api.get_sw_version(name="example")   # TypeError: got an unexpected keyword argument 'name'
    print(1)

    # 子类和父类函数调用，父类多种方法
    api.get_handler_object(handler="id1")  # 子类函数
    api.activate_plan(handler="id1")  # 父类函数1
    api.activate_plan(instrument_id="id1")  # 父类函数2,支持instrument_id
    api.activate_plan(conn1)  # 父类函数3，参数支持直接QueueHandler对象，通常不行：因为两个参数 timeout, handler

    # 重复创建测试
    # conn2 = api.connect_to(instrument_id="id3", blocker_ip="localhost")
    # conn3 = api.connect_to(instrument_id="id3", blocker_ip="localhost")
    # print(conn1)
    # print(conn2)
    # print(conn3)
    # api.connect_to(instrument_id="id3", blocker_ip="localhost")
    # api.get_handler_object(handler="id3")

    # dispatch_queue


    # 构造数据
    with open("config_tx.json", 'r') as f:
        rx_config = json.load(f)
    res = JSONObject()
    res.append_object(name="type", parameters="sa")
    # res.append_object(name="testing_duration", parameters=0)
    res.append_object(name="json_config", parameters=rx_config)
    # 执行dispatch
    con2 = api.attach(instrument_id="id2", blocker_ip="localhost")
    # api.dispatch_queue(res,handler="id2") # 方式1
    api.dispatch_queue(res,instrument_id="id2") # 方式2
    # api.dispatch_queue(res,con2) # 方式3

    # tx
    print(res.objects["json_config"]['tester_config']["analyzer"]["device_address"])
    # rx
    with open("config_rx.json", 'r') as f:
        rx_config = json.load(f)
    res = JSONObject()
    res.append_object(name="type", parameters="sg")
    res.append_object(name="testing_duration", parameters=60)
    res.append_object(name="json_config", parameters=rx_config)
    print(res.objects["json_config"]['tester_config']["generator_combinations"]["wanted_signal_generator_1"]["device_address"])


