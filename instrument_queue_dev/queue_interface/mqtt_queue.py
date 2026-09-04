# debug【最简】【挂起】
# import paho.mqtt.client as paho
# def on_message(mosq, obj, msg):
#     print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
# client = paho.Client()
# client.on_message = on_message
# client.connect("127.0.0.1", 1883, 60)
# # client.subscribe("job_done/result/127.0.0.1", 0)
# client.subscribe("job_done/result/#", 0)
# client.loop_forever()
#
#
#
#
# 【挂起】
# import paho.mqtt.client as paho
#
#
# def on_message(mosq, obj, msg):
#     print(obj)
#     print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
#     mosq.publish('pong', 'ack', 0)
#
#
# def on_publish(mosq, obj, mid):
#     print(mosq, obj, mid)
#     pass
#
#
# client = paho.Client()
# client.on_message = on_message
# client.on_publish = on_publish
#
# # client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
# client.connect("127.0.0.1", 1883, 60)
#
# client.subscribe("kids/yolo", 0)
# client.subscribe("lock_res/#", 0)
#
# # 方式1
# # while client.loop() == 0:
# #     pass
# # 方式2
# client.loop_forever()
#
#
# simple方式 【挂起】【收到后退出】
# import paho.mqtt.subscribe as subscribe
#
# topics = ['#']
#
# m = subscribe.simple(topics, hostname="127.0.0.1", retained=False, msg_count=2)
#
# for a in m:
#     print(a.topic)
#     print(a.payload)
#

import time


# call back 【挂起】【收到后退出】
import paho.mqtt.subscribe as subscribe


# def print_msg(client, userdata, message):
#     print("%s : %s" % (message.topic, message.payload))


# def success_callback_for_topic(client, userdata, message):
#     print("%s : %s" % (message.topic, message.payload))
#
#
# def timeout_callback_for_topic(client, userdata, message):
#     print("%s : %s" % (message.topic, message.payload))
#
#
# @func_set_timeout(20)
# def waite_res_available_topic():
#     subscribe.callback(success_callback_for_topic, "#", hostname="127.0.0.1")


import queue
import threading
import paho.mqtt.subscribe as subscribe

from instrument_queue_dev.exceptions.exceptions import MsgReceived
from func_timeout import func_set_timeout, FunctionTimedOut


class MqttSubscribe:
    def __init__(self, hostname="127.0.0.1", timeout=5, topic="#"):
        self.hostname = hostname
        self.timeout = timeout  # 显示等待超时时间
        self.received = False
        self.topic = topic
        self.received_msg = (None, None)
        self.msg_q = queue.Queue()

    @staticmethod
    def print_msg(client, userdata, message):
        print("%s : %s" % (message.topic, message.payload))

    def success_callback_for_topic(self, client, userdata, message):
        # print("%s : %s" % (message.topic, message.payload))
        self.received = True
        self.received_msg = message.topic, message.payload
        # return message.topic, message.payload

    def callback_for_topic_not_received(self, message):
        # MsgReceived
        if self.received:
            print("Msg has received , exit waiting !")
            return 0
            # raise MsgReceived("Msg has received , exit waiting !")

        # not MsgReceived
        print(message)
        return -1

    # # @func_set_timeout(self.timeout)  # 【不行】name 'self' is not defined 错误
    # @func_set_timeout(20)
    # def waite_res_available_topic(self):
    #     subscribe.callback(self.success_callback_for_topic, "#", hostname=self.hostname)

    # 显示等待
    def waite_res_available_topic(self, explicit_timeout=180):
        # @func_set_timeout(self.timeout)
        @func_set_timeout(explicit_timeout)
        def _waite_res_available_topic():
            subscribe.callback(self.success_callback_for_topic, self.topic, hostname=self.hostname)

        return _waite_res_available_topic()

    # 隐式等待
    def waite_res_available_topic_implicit(self,implicit_timeout=180):
        threading.Thread(target=self._implicit_waits, daemon=True).start()
        self.received_msg = self.msg_q.get(timeout=implicit_timeout) # 隐式等待超时时间


    def _implicit_waits(self):
        subscribe.callback(self.on_receive_message, self.topic, hostname=self.hostname)


    def on_receive_message(self, _, __, message):
        print("Msg has received , exit waiting !")
        self.msg_q.put((message.topic, message.payload))



class InstrumentMqttMsg:
    def __init__(self, mqtt_sub: MqttSubscribe):
        self.mqtt_sub = mqtt_sub


    def get_received_msg(self):
        return self.mqtt_sub.received_msg

    def lock_instrument(self, msg="No Msg Received!",timeout=180):
        rc = -1
        # wait topic
        try:
            self.mqtt_sub.waite_res_available_topic(explicit_timeout=timeout)
        # callback for topic not received
        except FunctionTimedOut:
            rc = self.mqtt_sub.callback_for_topic_not_received(msg)
        # after msg received action !
        except MsgReceived:
            pass
        except Exception:
            raise
        finally:
            return rc, self.get_received_msg()


    def lock_instrument_implicit_waits(self, msg="No Msg Received!",timeout=180):
        rc = -1
        # wait topic
        try:
            self.mqtt_sub.waite_res_available_topic_implicit(implicit_timeout=timeout)
        # callback for topic not received
        except FunctionTimedOut:
            rc = self.mqtt_sub.callback_for_topic_not_received(msg)
        # after msg received action !
        except MsgReceived:
            pass
        except Exception:
            raise
        finally:
            return rc,self.get_received_msg()



# TODO 删除 __main__
if __name__ == '__main__':

    # mq_sub = MqttSubscribe(hostname="127.0.0.1", timeout=10,topic="#")
    # mq_sub = MqttSubscribe(hostname="127.0.0.1", timeout=10, topic="job_done/#")

    # 显示等待
    # mq_sub = MqttSubscribe(hostname="127.0.0.1", topic="job_done/#")
    # instr = InstrumentMqttMsg(mq_sub)
    # rc, (msg_topic, msg_payload) = instr.lock_instrument(timeout=60)  # 前面的括号不能省
    # import pickle
    # print(pickle.loads(msg_payload))

    # 隐式等待
    mq_sub = MqttSubscribe(hostname="127.0.0.1", topic="job_done/#")
    instr = InstrumentMqttMsg(mq_sub)
    rc, (msg_topic, msg_payload) = instr.lock_instrument_implicit_waits()  # 前面的括号不能省
    import pickle
    print(pickle.loads(msg_payload))