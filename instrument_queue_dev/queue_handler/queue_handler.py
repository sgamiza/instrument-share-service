import pickle
import time
import queue
import threading
import json
import logging
import paho.mqtt.publish as publish
from instrument_queue_dev.exceptions.exceptions import InsrumentTypeNotFound,DeviceControlFailed
from instrument_queue_dev.instrument_control.instrument_interface import ConductedSignalQuality
from instrument_queue_dev.storage.stores_interface import JSONObject
from instrument_queue_dev.rfswitch_control import TopYoung
from instrument_queue_dev.instrument_control.prel3_tm_rx_sg_result import stop_sg
from pyvisa.errors import VisaIOError


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# tpy = TopYoung.TopYoung()


# TODO 关键 2023-04-24 实现sg和sa的绑定，可以创建多个这个对象，instrument_id唯一识别
class QueueHandler(object):
    # 状态码和默认值
    STATUS_OK = {"STATUS": "OK"}
    STATUS_ERR = {"STATUS": "ERROR"}
    DEFAULT_INSTRUMENT_HOLD_TIME = 0

    # 推荐ip作为唯一instrument_id
    def __init__(self, instrument_id: str,
                 mqtt_blocker_ip: str = "localhost"):
        self.conducted_signal_quality = ConductedSignalQuality()
        self.instrument_id = instrument_id
        # mqtt
        self.mqtt_blocker_ip = mqtt_blocker_ip
        self.mqtt_msg_id: str = ""
        # queue
        self.result_q = queue.Queue()
        self.dispatch_q = queue.Queue()
        # start service
        self._start_notification_service()
        self._start_dispatch_service()

    def dispatch(self):
        while True:
            self._dispatch()

    # def dispatch(self, task_lock_request):
    def _dispatch(self):

        task_lock_request: JSONObject.objects = self.dispatch_q.get()
        # 方式1 【默认值设置1】
        try:
            instrument_hold_time = task_lock_request["testing_duration"]
        except KeyError:
            instrument_hold_time = self.DEFAULT_INSTRUMENT_HOLD_TIME

        # 方式2 【默认值设置2】
        # 最好不用 self.instrument_id 最好为msg id ，采用的是uuid4
        self.mqtt_msg_id = task_lock_request["mqtt_msg_id"] \
            if task_lock_request.get("mqtt_msg_id") else self.instrument_id  # get 需要重写 dict

        # print("debug msg1:", self.mqtt_msg_id)

        try:
            instrument_type = task_lock_request["type"]
        except KeyError:
            raise InsrumentTypeNotFound


        instrument_config = {
            'testing_duration': instrument_hold_time,
            # 仪表配置文件
            'json_config': task_lock_request["json_config"],
        }

        if not "simple_reserve" == instrument_type:

            # TODO rpc实现交换机切换
            try:
                # tpy不能设置成全局的
                tpy = TopYoung.TopYoung()
                rf_switch_ip = task_lock_request["rf_switch_ip"]
                rf_switch_port = task_lock_request["rf_switch_port"]
                # print()
                print("rf_switch_ip:", rf_switch_ip)
                print("rf_switch_port:", rf_switch_port)

                # rf switch
                # tpy.rf_switch_TSS32T1_close_port(rf_switch_ip, rf_switch_port)

                if len(rf_switch_port) < 2:
                    # rf switch
                    tpy.rf_switch_TSS32T1_close_port(rf_switch_ip, *rf_switch_port)
                else:
                    # PA
                    tpy.set_one_PA_port_close_32x16(rf_switch_ip, *rf_switch_port)

            # 同一个pc，连续操rf switch会报错
            except KeyError:
                logger.warning(f'rf switch is not changing !')
                # raise后对应的队列无法工作
                # 比如 sa raise后，后续的sa直接就不工作了
                raise

            except DeviceControlFailed:
                logger.error(f'rf switch exec cmd failed !')

        # 处理 simple_reserve
        else:
            pass

        # 仪表处理
        # 等待外边处理
        # self._instrument_processing(instrument_type, instrument_config)
        # 等待里面处理
        self._instrument_processing(instrument_type, instrument_config, instrument_hold_time)

        # TODO 队列可视化
        # xxx

        # TODO 设备保持
        # 设备保持测试一段时间,SG需要发送一会儿等测试结束
        # 需要移到 仪表处理 队列内部
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # self._hold_instrument(instrument_hold_time)

    @classmethod
    def _hold_instrument(cls, instrument_hold_time):
        logger.warning(f'设备将要保持{instrument_hold_time}秒！')
        logger.info(f'设备保持...')
        time.sleep(instrument_hold_time)
        logger.info(f'保持结束！')

    def _instrument_processing(self, instrument_type, instrument_config, instrument_hold_time=None):

        if "sg" == instrument_type:
            if not instrument_hold_time:
                raise InsrumentTypeNotFound
            print("sg is doing job")
            instrument_res = self.conducted_signal_quality.run_sg(instrument_config)
            print("sg结果：" + str(instrument_res))
            # 先发送结果，再设备保持，不然客户端无法读取结果
            self.result_q.put(instrument_res)
            # 设备保持时间
            self._hold_instrument(instrument_hold_time)
            # sg 关闭发送信号
            # self._instrument_teardown("sg", instrument_config)
            self._instrument_teardown(self, "sg", instrument_config)

        elif "sa" == instrument_type:
            print("sa is doing job")
            instrument_res = self.conducted_signal_quality.run_sa(instrument_config)
            print("sa结果：" + str(instrument_res))
            self.result_q.put(instrument_res)

            # TODO 方案2 SA设备保持时间 2023-04-13
            self._hold_instrument(instrument_hold_time if instrument_hold_time else 0)

            # sa 关闭
            # 报错少参数
            # self._instrument_teardown("sa", instrument_config)
            # 不报错 classmethod
            # self._hold_instrument(instrument_hold_time)
            # 不报错 staticmethod
            self._instrument_teardown(self, "sa", instrument_config)



        elif "simple_reserve" == instrument_type:
            if not instrument_hold_time:
                raise InsrumentTypeNotFound
            print("simple_reserve is doing job")
            instrument_res = self.conducted_signal_quality.run_simple_instrument_reserve(instrument_config)
            print("simple_reserve结果：" + str(instrument_res))
            # 先发送结果，再设备保持，不然客户端无法读取结果
            self.result_q.put(instrument_res)
            # 设备保持时间
            self._hold_instrument(instrument_hold_time)

            self._instrument_teardown(self, "simple_reserve", instrument_config)


        else:
            raise InsrumentTypeNotFound

    @staticmethod
    def _instrument_teardown(cls, instrument_type, instrument_config):

        if "sg" == instrument_type:
            print("sg teardown ...")
            try:
                stop_sg(instrument_config["json_config"])
            except VisaIOError:
                logger.error("设备连接异常！")
                # raise
            except RuntimeError:
                logger.error("同步信号设置失败！")
            print("sg teardown done")

        elif "sa" == instrument_type:
            print("sa teardown done")

        elif "simple_reserve" == instrument_type:
            print("simple_reserve teardown done")

        else:
            raise InsrumentTypeNotFound

    # mqtt 通知函数
    def _start_notification_service(self):
        threading.Thread(target=self._mqtt_notification, args=("msg_id",), daemon=True).start()

    #  dispatch
    def _start_dispatch_service(self):
        # threading.Thread(target=self.dispatch, args=("test_str",))
        threading.Thread(target=self.dispatch, daemon=True).start()

    def add_to_queue(self, task_lock_request):
        self.dispatch_q.put(task_lock_request)

    def _mqtt_notification(self, msg_id=None):
        while True:
            result_playload = dict()
            instrument_res = self.result_q.get()
            result_playload["result"] = instrument_res

            if isinstance(instrument_res, Exception):
                result_playload.update(self.STATUS_ERR)
            else:
                result_playload.update(self.STATUS_OK)

            # print('debug: ',instrument_res) # mqtt result test
            msg_payload = pickle.dumps(result_playload)
            # 设置 qos=1, retain=False
            publish.single(topic="job_done/result/%s" % self.mqtt_msg_id,
                           payload=msg_payload,
                           qos=1,
                           hostname=self.mqtt_blocker_ip)
            logger.info(f"MQTT：msg has sent for job done!")


# TODO 删除 __main__
if __name__ == '__main__':

    # 构造数据
    with open("config_tx.json", 'r') as f:
        rx_config = json.load(f)
    res = JSONObject()
    res.append_object(name="type", parameters="sa")
    # res.append_object(name="testing_duration", parameters=0)
    res.append_object(name="json_config", parameters=rx_config)
    # 执行dispatch
    queue_handler = QueueHandler("instrument_id", mqtt_blocker_ip="localhost")
    queue_handler.dispatch(res)
