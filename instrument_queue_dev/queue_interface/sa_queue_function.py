
import pickle
import json
import uuid

from instrument_queue_dev.storage.stores_interface import JSONObject
from instrument_queue_dev.queue_interface.mqtt_queue import MqttSubscribe, InstrumentMqttMsg
from instrument_queue_dev.queue_interface.queue_server import InstrumentQueueManager

# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
InstrumentQueueManager.register('task_lock_request')


def get_task_queue(server_addr='127.0.0.1'):
    # 连接到服务器，也就是运行task_master.py的机器:
    # server_addr = '127.0.0.1'
    print('Connect to server %s...' % server_addr)

    # 端口和验证码注意保持与task_master.py设置的完全一致:
    m = InstrumentQueueManager(address=(server_addr, 5000), authkey=b'YOUR_AUTHKEY')
    # 从网络连接:
    m.connect()
    # 获取Queue的对象:
    lock_request = m.task_lock_request()
    return lock_request


def send_config_to_task_queue(file_path, task_queue, rf_switch_ip,
                              rf_switch_port, testing_duration=None):

    # 请求仪表进行TM测试:
    with open(file_path, 'r') as f:
        rx_config = json.load(f)
    res = JSONObject()
    res.append_object(name="type", parameters="sa")
    # 设备不需要等待，读取结果直接返回
    # res.append_object(name="testing_duration", parameters=0)
    res.append_object(name="json_config", parameters=rx_config)

    # rf switch config
    res.append_object(name="rf_switch_ip", parameters=rf_switch_ip)
    res.append_object(name="rf_switch_port", parameters=rf_switch_port)
    # 增加ip字段作为唯一instrument_id
    instrument_id = res.objects["json_config"]['tester_config']["analyzer"]["device_address"]
    res.append_object(name="instrument_id",
                      parameters=instrument_id)
    # msg id 才是唯一id
    mqtt_msg_id = str(uuid.uuid4())
    # print(mqtt_msg_id)
    res.append_object(name="mqtt_msg_id",
                      parameters=mqtt_msg_id)

    task_queue.put(res)
    print('lock_request finished, waiting for respose ..')
    return mqtt_msg_id


def waite_queue_mqtt_msg(hostname="127.0.0.1", topic="#", waite_timeout=20):
    # MQTT 等待仪表测试结果

    topic = "job_done/result/"+topic
    mq_sub = MqttSubscribe(hostname=hostname, timeout=waite_timeout, topic=topic)
    instr = InstrumentMqttMsg(mq_sub)

    # SG和SA对调一下等待方式 2023-04-06
    # 2023-04-12 非隐方式排队时间太长，同时等待的话可能超过10多分钟
    # rc, (msg_topic, msg_payload) = instr.lock_instrument(timeout=waite_timeout)

    # SA读取时间可能比较长，采用隐式等待
    # 2023-04-12 非隐方式排队时间太长，同时等待的话可能超过10多分钟
    rc, (msg_topic, msg_payload) = instr.lock_instrument_implicit_waits(timeout=waite_timeout)


    # print(rc)
    if msg_payload:
        msg_payload_dic = pickle.loads(msg_payload)
        # print(msg_payload_dic)
        return msg_payload_dic

        # instrument_status = msg_payload_dic["STATUS"]
        # instrument_result = msg_payload_dic["result"]
        # print(type(instrument_result))
    else:
        print("waite for sa time out!")
        return False


# TODO 删除 __main__
if __name__ == '__main__':

    q = get_task_queue(server_addr='127.0.0.1')

    # 仪表保持时间
    # TODO 不用json文件，直接传送关键参数,服务器导入相应的json
    smg_id = send_config_to_task_queue(file_path="config_tx.json", task_queue=q)
    # mqtt 等待时间 SA读取时间可能比较长
    # 隐式等待
    waite_queue_mqtt_msg(hostname="127.0.0.1", topic=smg_id, waite_timeout=200)

    # debug
    # 显示等待
    # waite_queue_mqtt_msg(hostname="127.0.0.1", topic=instrument_id, waite_timeout=20)
    # waite_queue_mqtt_msg(hostname="127.0.0.1",  waite_timeout=20)

    # import paho.mqtt.client as paho
    # def on_message(mosq, obj, msg):
    #     print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    # client = paho.Client()
    # client.on_message = on_message
    # client.connect("127.0.0.1", 1883, 60)
    # # client.subscribe("job_done/result/127.0.0.1", 0)
    # client.subscribe("job_done/result/#", 0)
    # client.loop_forever()

