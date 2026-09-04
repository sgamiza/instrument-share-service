
import json
import uuid
import pickle

# 执行包的__init__下文件就不需要如下的操作了
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from instrument_queue_dev.queue_interface.mqtt_queue import MqttSubscribe, InstrumentMqttMsg
from instrument_queue_dev.queue_interface.queue_server import InstrumentQueueManager
from instrument_queue_dev.storage.stores_interface import JSONObject


# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
InstrumentQueueManager.register('task_lock_request')


def get_task_queue(server_addr='127.0.0.1'):
    # 连接到服务器，也就是运行task_master.py的机器:
    # server_addr = '127.0.0.1'
    print('Connect to server %s...' % server_addr)

    # 端口和验证码注意保持与task_master.py设置的完全一致:
    # m = QueueManager(address=(server_addr, 5000), authkey=b'YOUR_AUTHKEY', serializer='pickle') # 方式1
    m = InstrumentQueueManager(address=(server_addr, 5000), authkey=b'YOUR_AUTHKEY') # 方式2
    # 从网络连接:
    m.connect()
    # 获取Queue的对象:
    lock_request = m.task_lock_request()
    return lock_request


def send_config_to_task_queue(file_path, testing_duration,
                              rf_switch_ip, rf_switch_port, task_queue):

    # 请求SG进行TM测试rx:
    with open(file_path, 'r') as f:
        rx_config = json.load(f)
    res = JSONObject()
    res.append_object(name="type", parameters="sg")
    # SG 发送信号持续时间
    res.append_object(name="testing_duration", parameters=testing_duration)
    res.append_object(name="json_config", parameters=rx_config)

    # rf switch config
    res.append_object(name="rf_switch_ip", parameters=rf_switch_ip)
    res.append_object(name="rf_switch_port", parameters=rf_switch_port)
    # 增加ip字段作为唯一instrument_id
    instrument_id = res.objects["json_config"]['tester_config']["generator_combinations"]["wanted_signal_generator_1"][
        "device_address"]
    res.append_object(name="instrument_id",
                      parameters=instrument_id)
    # msg id 才是唯一id

    mqtt_msg_id = str(uuid.uuid4())
    # print(mqtt_msg_id)
    res.append_object(name="mqtt_msg_id",
                      parameters=mqtt_msg_id)

    task_queue.put(res)
    print('lock_request finished, waiting for respose ..')
    # return instrument_id
    return mqtt_msg_id


def waite_queue_mqtt_msg(hostname="127.0.0.1", topic="#", waite_timeout=20):
    # MQTT 等待SG发送数据
    topic = "job_done/result/" + topic
    mq_sub = MqttSubscribe(hostname=hostname, timeout=waite_timeout, topic=topic)
    instr = InstrumentMqttMsg(mq_sub)

    # 显示等待 2023-04-06 如果显示等待的话run_client_sg.py中 res_waite_timeout必须>sg_testing_hold_time 不然直接超时错误
    # rc, (msg_topic, msg_payload) = instr.lock_instrument(timeout=waite_timeout)
    # 隐式等待 sg 必须隐式等待 2023-04-06
    rc, (msg_topic, msg_payload) = instr.lock_instrument_implicit_waits(timeout=waite_timeout)


    # print(rc)
    if msg_payload:
        # SG 发送数据成功
        msg_payload_dic = pickle.loads(msg_payload)
        # {'result': [{'cell_id': 1, 'level': -50.0, 'error_rate': None}], 'STATUS': 'OK'}
        # print(msg_payload_dic)
        return msg_payload_dic

        # instrument_status = msg_payload_dic["STATUS"]
        # instrument_result = msg_payload_dic["result"]
        # if "OK" == instrument_status and instrument_result:
        #     # 仪表发送成功
        #     return instrument_result
        # return False


        # BBU读取数据,不在这里实现
        # print("读取BBU上行throughput...")
    else:
        # SG 设置失败
        print("waite for sg time out!")
        return False


# TODO 删除 __main__
if __name__ == '__main__':
    # testing_duration 需要大于 waite_timeout
    q = get_task_queue(server_addr='127.0.0.1')
    # 仪表保持时间 testing_duration
    smg_id = send_config_to_task_queue(file_path="config_rx.json", testing_duration=60, task_queue=q)
    # mqtt 等待时间 waite_timeout, SG执行速度快
    waite_queue_mqtt_msg(hostname="127.0.0.1", topic=smg_id, waite_timeout=30)


