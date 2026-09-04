
import json
import uuid
import pickle
from instrument_queue_dev.queue_interface.mqtt_queue import MqttSubscribe, InstrumentMqttMsg
from instrument_queue_dev.queue_interface.queue_server import InstrumentQueueManager
from instrument_queue_dev.storage.stores_interface import JSONObject


InstrumentQueueManager.register('task_lock_request')


def get_task_queue(server_addr='127.0.0.1'):

    print('Connect to server %s...' % server_addr)
    m = InstrumentQueueManager(address=(server_addr, 5000), authkey=b'YOUR_AUTHKEY')
    m.connect()
    lock_request = m.task_lock_request()
    return lock_request


# args change for simple_reserve 2023-04-23
def send_config_to_task_queue(instrument_id, testing_duration, task_queue):
    res = JSONObject()
    res.append_object(name="type", parameters="simple_reserve")
    # 适配
    res.append_object(name="json_config", parameters=None)
    # 持续时间
    res.append_object(name="testing_duration", parameters=testing_duration)
    res.append_object(name="instrument_id", parameters=instrument_id)
    # msg id 才是唯一id
    mqtt_msg_id = str(uuid.uuid4())
    res.append_object(name="mqtt_msg_id",parameters=mqtt_msg_id)
    task_queue.put(res)

    print('lock_request finished, waiting for respose ..')
    return mqtt_msg_id



def waite_queue_mqtt_msg(hostname="127.0.0.1", topic="#", waite_timeout=20):
    # MQTT 等待SG发送数据
    topic = "job_done/result/" + topic
    mq_sub = MqttSubscribe(hostname=hostname, timeout=waite_timeout, topic=topic)
    instr = InstrumentMqttMsg(mq_sub)

    # print(topic)

    rc, (msg_topic, msg_payload) = instr.lock_instrument_implicit_waits(timeout=waite_timeout)


    # print(rc)
    if msg_payload:
        # SG 发送数据成功
        msg_payload_dic = pickle.loads(msg_payload)
        # {'result': [SensitivityResult(cell_id=1, level=-50.0, error_rate=None)], 'STATUS': 'OK'}
        # print(msg_payload_dic)
        return msg_payload_dic

        # instrument_status = msg_payload_dic["STATUS"]
        # instrument_result = msg_payload_dic["result"]
        # if "OK" == instrument_status and isinstance(instrument_result, SensitivityResult):
        #     # 仪表发送成功
        #     return instrument_result
        # return False


        # BBU读取数据,不在这里实现
        # print("读取BBU上行throughput...")
    else:
        # SG 设置失败
        print("waite time out!")
        return False




# TODO 删除 __main__
if __name__ == '__main__':
    # testing_duration 需要大于 waite_timeout
    q = get_task_queue(server_addr='127.0.0.1')
    # 仪表保持时间 testing_duration
    smg_id = send_config_to_task_queue(file_path="config_rx.json", testing_duration=60, task_queue=q)
    # mqtt 等待时间 waite_timeout, SG执行速度快
    waite_queue_mqtt_msg(hostname="127.0.0.1", topic=smg_id, waite_timeout=30)


