

"""Queue For Instrument Server

The client sends json to the server, and the server returns a status code after processing,The server automatically creates the corresponding queue according to the IP of the instruments, and each instruments maintains its own queue
The client monitors the corresponding processing results
The client does not need to install the instrument library, which is convenient for deployment
Unified maintenance on the server side to facilitate management (instrument connection, operation, etc.)
The server returns the test result if successful, and the server needs to return the error and the reason to the client if the server is abnormal
The client can set the queuing waiting time and return after timeout
The client sets the device usage time（ the SG needs to continue to send signals for a period of time）
rf switch conreol supported
robot supported  for the client


- 客户端发送json到server，server处理后返回状态码，
- server根据仪表IP自动创建对应的队列，每个仪表维护自己的队列
- client监听对应的处理结果
- 服务器成功需要返回测试结果，服务器异常需要返回错误以及原因给客户端
- 客户端可以设置排队等待时间，超时返回
- 客户端设置设备使用时间，SG需要持续一段时间发信号
- 客户端无需安装仪表库，方便部署
- 环境多的时候不用针对不同的仪表增加各种配置
- 队列需要实现sg保持后停止发流，需要实现接口，或者通过rfswitch停止
- 剥离client，封装成robot
- 整合到原来的TM test case，实际环境调试



# TODO
- robot case 增加异常处理，超时读取错误等
- sg修改, sa [aclr,power等]合入

- 简单的SG保持功能，适应beamset的功能

- result返回的问题
- calibration文件夹对应不同的校验文件的问题


- rf 操作错误，不同仪表相同的rf switch错误处理【同时操作有bug】
- rf switch 队列？ 和仪表队列同步？
- 不用json文件，直接传送关键参数,服务器自动导入相应仪表类型的json
- pattern ID 同上，或者BTS直接获取
- 帧配比直接映射到A3，A5等，方便使用
- RF Switch 动态调用,RPC实现，自适应不同rf switch
- server 分布式
- 优先级队列
- rf 不支持多个同时设置
- 同一个仪表队列非常长，排队时间如何优化？
- 问题都出在server端，后续调试维护问题？



# TODO 2
- server 待处理队列可查询，可视化
- 等待超时的job退出server队列

"""

# 全路径也行 instrument_queue_dev
# from instrument_queue_dev.queue_interface.queue_server import create_queue
from queue_interface.queue_server import (create_queue,
                                          queue_callable,
                                          request_dispatch_by_instrument_id)

from queue_interface.sg_queue_function import get_task_queue as sg_get_task_queue
from queue_interface.sg_queue_function import send_config_to_task_queue as sg_send_config_to_task_queue
from queue_interface.sg_queue_function import waite_queue_mqtt_msg as sg_waite_queue_mqtt_msg
from queue_interface.sa_queue_function import get_task_queue as sa_get_task_queue
from queue_interface.sa_queue_function import send_config_to_task_queue as sa_send_config_to_task_queue
from queue_interface.sa_queue_function import waite_queue_mqtt_msg as sa_waite_queue_mqtt_msg

from queue_interface.simple_reserve_queue_function import get_task_queue as simple_reserve_get_task_queue
from queue_interface.simple_reserve_queue_function import send_config_to_task_queue as simple_reserve_send_config_to_task_queue
from queue_interface.simple_reserve_queue_function import waite_queue_mqtt_msg as simple_reserve_waite_queue_mqtt_msg

from queue_handler.queue_handler_manager import QueueHandlerManager
from instrument_queue_dev.exceptions.exceptions import InsrumentTypeNotFound


__version__ = '1.0.0'
__all__ = ['run_server', 'run_client']



# TODO 删除 run_server, 保留linux
def run_server(ip="localhost"):

    # blocker_ip = "localhost"
    # blocker_ip = "0.0.0.0"
    # blocker_ip = "127.0.0.1"

    # 创建 task_lock_request 监听任务
    # qm, q_task_lock_request = create_queue("task_lock_request", queue_callable)
    qm, q_task_lock_request = create_queue("task_lock_request", queue_callable, queue_address=ip)
    count = 0
    api = QueueHandlerManager()

    while True:
        # instrument_ip = "default ip"
        count += 1
        print(str(count) + "*" * 100)
        # result_playload = {}
        # instrument_hold_time = 0
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
        request_dispatch_by_instrument_id(api, r, blocker_ip=ip)


def run_server_linux(ip="localhost"):

    qm, q_task_lock_request = create_queue("task_lock_request", callback=lambda: queue_callable, queue_address=ip)

    count = 0
    api = QueueHandlerManager()

    while True:
        count += 1
        print("linux"+str(count) + "*" * 100)
        r = q_task_lock_request.get()

        request_dispatch_by_instrument_id(api, r, blocker_ip=ip)



def run_client(server_type, server_addr,
               config_file, res_waite_timeout,
               rf_switch_ip, rf_switch_port,
               sg_testing_hold_time=60):

    queue_server_ip = mqtt_server_ip = server_addr

    # 显示等待
    if "sg" == server_type:
        # testing_duration 需要大于 waite_timeout
        q = sg_get_task_queue(server_addr=queue_server_ip)

        # 仪表保持时间 testing_duration，file_path="config_rx.json"
        # 队列需要增加的内容，sg保持，rf switch ip等
        smg_id = sg_send_config_to_task_queue(file_path=config_file, testing_duration=sg_testing_hold_time,
                                              rf_switch_ip=rf_switch_ip, rf_switch_port=rf_switch_port, task_queue=q)
        # mqtt 等待时间 waite_timeout, SG执行速度快，default waite_timeout=30
        return sg_waite_queue_mqtt_msg(hostname=mqtt_server_ip, topic=smg_id, waite_timeout=res_waite_timeout)

    # 隐式等待
    if "sa" == server_type:
        q = sa_get_task_queue(server_addr=queue_server_ip)
        # 仪表保持时间
        # TODO 不用json文件，直接传送关键参数,服务器导入相应的json

        # file_path="config_tx.json"
        smg_id = sa_send_config_to_task_queue(file_path=config_file, rf_switch_ip=rf_switch_ip,
                                              rf_switch_port=rf_switch_port, task_queue=q)
        # mqtt 等待时间 SA读取时间可能比较长
        # 隐式等待 default waite_timeout=200
        return sa_waite_queue_mqtt_msg(hostname=mqtt_server_ip, topic=smg_id, waite_timeout=res_waite_timeout)



    # if "simple_reserve" == server_type:
    #     q = simple_reserve_get_task_queue(server_addr=queue_server_ip)
    #     smg_id = simple_reserve_send_config_to_task_queue(file_path=None, testing_duration=sg_testing_hold_time,
    #                                           rf_switch_ip=rf_switch_ip, rf_switch_port=rf_switch_port, task_queue=q)
    #     # mqtt 等待时间 waite_timeout, SG执行速度快，default waite_timeout=30
    #     return simple_reserve_waite_queue_mqtt_msg(hostname=mqtt_server_ip, topic=smg_id, waite_timeout=res_waite_timeout)


    # 不raise会导致robot直接pass , 如果传入的参数可能多了标点什么的
    raise InsrumentTypeNotFound



def run_client_simple_reserve(server_addr, instrument_id, res_waite_timeout, hold_time):

    queue_server_ip = mqtt_server_ip = server_addr

    q = simple_reserve_get_task_queue(server_addr=queue_server_ip)
    smg_id = simple_reserve_send_config_to_task_queue(instrument_id=instrument_id, testing_duration=hold_time, task_queue=q)

    return simple_reserve_waite_queue_mqtt_msg(hostname=mqtt_server_ip, topic=smg_id,waite_timeout=res_waite_timeout)






# TODO 删除 __main__
if __name__ == '__main__':

    run_server()
