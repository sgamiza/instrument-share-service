import time
import queue
import logging
import threading

from instrument_queue_dev.instrument_control.prel3_tm_tx_sa_result import run_rf_measurement_sa
from instrument_queue_dev.instrument_control.prel3_tm_rx_sg_result import run_rf_measurement_sg
from instrument_queue_dev.instrument_control.prel3_simple_instrument_reserve import run_simple_instrument_reserve

logger = logging.getLogger(__name__)


class ConductedSignalQuality:

    def __init__(self):
        self.sg_queue_size = 0
        self.sg_q = queue.Queue()
        self.sa_queue_size = 0
        self.sa_q = queue.Queue()
        self.simple_instrument_reserve_queue_size = 0
        self.simple_instrument_reserve_q = queue.Queue()
        self.empty_queues()
        self.result_q = queue.Queue()
        self.start_service_for_sa_and_sg()
        self.start_service_for_simple_instrument_reserve()

    def run_sa(self, sa_data, loops: int = 1):
        logger.info("START SA MEASUREMENT")
        results = self._get_signal_analysis_result(sa_data, loops)
        return results

    def run_sg(self, sg_data, loops: int = 1):
        logger.info("START SG Testing")
        results = self._get_signal_generator_result(sg_data, loops)
        return results

    def run_simple_instrument_reserve(self, simple_instrument_data, loops: int = 1):
        logger.info("START run_simple_instrument_reserve")
        results = self._get_simple_instrument_reserve_result(simple_instrument_data, loops)
        return results


    def empty_queues(self):
        self.sa_q.empty()
        self.sg_q.empty()
        self.simple_instrument_reserve_q.empty()


    def start_service_for_sa_and_sg(self):
        threading.Thread(target=self._analysis_worker, daemon=True).start()
        threading.Thread(target=self._generator_worker, daemon=True).start()


    def start_service_for_simple_instrument_reserve(self):
        threading.Thread(target=self._simple_instrument_reserve_worker, daemon=True).start()



    def _get_signal_analysis_result(self, sa_data, loops=1):

        try:
            for i in range(loops):
                loop_count = i
                logger.info(f'Measurement loops: {i + 1}/{loops}')
                # bool
                stop_analysis_worker = (loop_count == loops - 1)
                sa_data.update({"stop_command": stop_analysis_worker})
                # 发送到worker
                self._send_to_sa_queue(**sa_data)
        except Exception as err:
            logger.error(f'Error in Signal Quality measurement: {err}')
            raise RuntimeError(f'Error in Signal Quality measurement: {err}')
        finally:
            pass

        while self.sa_queue_size > 0:
            # logger.info(f'analysis job is in progressing, remaining job: {self.sa_queue_size}')
            logger.info(f'SA for prel3 is progressing, please waite')
            time.sleep(5)
        # 等待job done消息
        self.sa_q.join()

        # get result
        results = self.result_q.get()
        return results

    def _get_signal_generator_result(self, sg_data, loops=1):

        try:
            for i in range(loops):
                loop_count = i
                logger.info(f'Measurement loops: {i + 1}/{loops}')
                # bool
                stop_analysis_worker = (loop_count == loops - 1)
                sg_data.update({"stop_command": stop_analysis_worker})
                # 发送到worker
                self._send_to_sg_queue(**sg_data)
        except Exception as err:
            logger.error(f'Error in Signal Quality measurement: {err}')
            raise RuntimeError(f'Error in Signal Quality measurement: {err}')
        finally:
            pass

        while self.sg_queue_size > 0:
            # logger.info(f'generator job is in progressing, remaining job: {self.sg_queue_size}')
            logger.info(f'SG for prel3 is progressing, please waite')
            time.sleep(5)
        # 等待job done消息
        self.sg_q.join()

        # get result
        results = self.result_q.get()
        return results



    def _get_simple_instrument_reserve_result(self, data, loops=1):

        try:
            for i in range(loops):
                loop_count = i
                logger.info(f'Measurement loops: {i + 1}/{loops}')
                # bool
                stop_worker = (loop_count == loops - 1)
                data.update({"stop_command": stop_worker})
                # 发送到worker
                self._send_to_simple_instrument_reserve_queue(**data)

        except Exception as err:
            logger.error(f'Error in Signal Quality measurement: {err}')
            raise RuntimeError(f'Error in Signal Quality measurement: {err}')
        finally:
            pass

        while self.simple_instrument_reserve_queue_size > 0:
            # logger.info(f'generator job is in progressing, remaining job: {self.sg_queue_size}')
            logger.info(f'SG for prel3 is progressing, please waite')
            time.sleep(5)

        # 等待job done消息
        self.simple_instrument_reserve_q.join()

        # get result
        results = self.result_q.get()
        return results



    def _send_to_sa_queue(self, testing_duration, json_config, stop_command):

        data_2_queue = {
            'testing_duration': testing_duration,
            'json_config': json_config,
            'stop_command': stop_command
        }
        '''send data to worker for async processing... '''
        self.sa_q.put(data_2_queue)
        self.sa_queue_size = self.sa_queue_size + 1

    def _send_to_sg_queue(self, testing_duration, json_config, stop_command):

        data_2_queue = {
            'testing_duration': testing_duration,
            'json_config': json_config,
            'stop_command': stop_command
        }
        '''send data to worker for async processing... '''
        self.sg_q.put(data_2_queue)
        self.sg_queue_size = self.sa_queue_size + 1


    def _send_to_simple_instrument_reserve_queue(self, testing_duration, json_config, stop_command):

        data_2_queue = {
            'testing_duration': testing_duration,
            'json_config': json_config,
            'stop_command': stop_command
        }
        '''send data to worker for async processing... '''
        # self.sg_q.put(data_2_queue)
        # self.sg_queue_size = self.sa_queue_size + 1
        self.simple_instrument_reserve_q.put(data_2_queue)
        self.simple_instrument_reserve_queue_size = self.simple_instrument_reserve_queue_size + 1



    # 类初始化就起线程执行这个函数，获取self.q执行
    def _analysis_worker(self):
        # logger.info('I am signal analysis worker, I am born!')
        inner_loop = 0
        while True:
            try:
                inner_loop += 1
                # logger.info(f'Signal analysis worker: I am alive! Ready for doing job number: {inner_loop}')
                logger.info(f'SA ready for doing job number: {inner_loop}')
                data_from_queue = self.sa_q.get()
                # 执行queue任务
                termination = data_from_queue['stop_command']

                # sa signal_quality_config
                carriers_config = data_from_queue["json_config"]['carriers_config']
                tester_config = data_from_queue["json_config"]['tester_config']
                # sa signal_quality_config
                signal_quality_config = data_from_queue["json_config"]['signal_quality_config']
                obue_config = data_from_queue["json_config"]['obue_config']

                # print("queue获取： ", data_from_queue)
                print(f"\tSA 测试持续时间：{data_from_queue['testing_duration']}")
                print(f"\tSA 配置参数carriers_config：{carriers_config}")
                print(f"\tSA 配置参数tester_config：{tester_config}")
                print(f"\tSA 配置参数signal_quality_config：{signal_quality_config}")
                print(f"\tSA 配置参数obue_config：{obue_config}")

                logger.info(f"SA 处理中...")

                res = run_rf_measurement_sa(carriers_config, tester_config, signal_quality_config)
                logger.info(f"SA处理完成，放入result queue")

                # 放入结果队列
                print(res)
                self.result_q.put(res)
                # self.result_q.put("result:" + str(inner_loop))

                self.sa_q.task_done()
                self.sa_queue_size = self.sa_queue_size - 1
                logger.info(f'Signal analysis worker: job done ,number: {inner_loop}')
            except Exception as err:
                self.sa_q.task_done()
                self.sa_queue_size = self.sa_queue_size - 1
                logger.error(err)
                # 抛出异常给主进程，或者直接放入结果队列
                self.result_q.put(err)
                # raise  # 调试阶段尽量raise
            if termination:
                logger.info('All jobs are done, wating...')
                # logger.info('Signal analysis worker: All jobs are done, I am dying!')
                # break   # 不能死

    def _generator_worker(self):
        # logger.info('I am signal generator worker, I am born!')
        inner_loop = 0
        while True:
            try:
                inner_loop += 1
                # logger.info(f'Signal generator worker: I am alive! Ready for doing job number: {inner_loop}')
                logger.info(f'SG ready for doing job number: {inner_loop}')
                data_from_queue = self.sg_q.get()
                # 执行queue任务
                termination = data_from_queue['stop_command']

                # sg sensitivity_config
                carriers_config = data_from_queue["json_config"]['carriers_config']
                tester_config = data_from_queue["json_config"]['tester_config']
                # sg sensitivity_config
                signal_quality_config = data_from_queue["json_config"]['sensitivity_config']
                uplink_analysis_config = data_from_queue["json_config"]['uplink_analysis_config']  # t-gate

                # print("queue获取： ", data_from_queue)
                print(f"\tSG 测试持续时间：{data_from_queue['testing_duration']}")
                print(f"\tSG 配置参数carriers_config：{carriers_config}")
                print(f"\tSG 配置参数tester_config：{tester_config}")
                print(f"\tSG 配置参数signal_quality_config：{signal_quality_config}")
                print(f"\tSG 配置参数uplink_analysis_config：{uplink_analysis_config}")

                logger.info(f"SG 处理中...")

                '''
                # tm_rx_sensitivity_result_test
                rx_carriers_config = rx_config['carriers_config']
                rx_tester_config = rx_config['tester_config']
                # rx_tester_config['generator_combinations']['wanted_signal_generator_1']['calibration_data_file'] = os.path.join(tm_dir,"rx_inband_ws_antenna_port_1.cal")
                sensitivity_config = rx_config['sensitivity_config']
                uplink_analysis_config = rx_config['uplink_analysis_config']
                '''

                res = run_rf_measurement_sg(carriers_config, tester_config, signal_quality_config, uplink_analysis_config)
                logger.info(f"SG处理完成，放入result queue")
                # 放入结果队列
                print(res)
                self.result_q.put(res)
                # self.result_q.put("result:" + res)
                # self.result_q.put("result:" + str(inner_loop))

                self.sg_q.task_done()
                self.sg_queue_size = self.sg_queue_size - 1
                # logger.info(f'Signal generator worker: job done ,number: {inner_loop}')
            except Exception as err:
                self.sg_q.task_done()
                self.sg_queue_size = self.sg_queue_size - 1
                logger.error(err)
                # 异常直接放入结果队列
                self.result_q.put(err)
                # raise  # 调试阶段尽量raise，raise会导致_get_signal_generator_result一直挂住
            if termination:
                logger.info('All jobs are done, wating...')


    # TODO SA 自定义函数 2023-04-13
    def _simple_instrument_reserve_worker(self):
        while True:
            try:
                logger.info(f'do simple instrument reserve job')
                # data_from_queue = self.sa_q.get()
                data_from_queue = self.simple_instrument_reserve_q.get()
                # 执行queue任务
                termination = data_from_queue['stop_command']

                # print("queue获取： ", data_from_queue)
                # print(f"\t simple_instrument_reserve 测试持续时间：{data_from_queue['testing_duration']}")

                logger.info(f"simple_instrument_reserve 处理中...")

                # TODO 自定义函数返回结果
                res = run_simple_instrument_reserve()
                logger.info(f"simple_instrument_reserve done")

                # 放入结果队列
                print(res)
                self.result_q.put(res)
                self.simple_instrument_reserve_q.task_done()
                # self.sa_queue_size = self.sa_queue_size - 1
                self.simple_instrument_reserve_queue_size = self.simple_instrument_reserve_queue_size - 1


            except Exception as err:
                self.simple_instrument_reserve_q.task_done()
                self.simple_instrument_reserve_queue_size = self.simple_instrument_reserve_queue_size - 1
                logger.error(err)
                # 抛出异常给主进程，或者直接放入结果队列
                self.result_q.put(err)
                # raise  # 调试阶段尽量raise
            if termination:
                logger.info('All jobs are done, wating...')
                # logger.info('Signal analysis worker: All jobs are done, I am dying!')
                # break   # 不能死





conducted_signal_quality = ConductedSignalQuality()



# TODO 删除 __main__
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s")

    # c = ConductedSignalQuality()

    import json

    with open("config_tx.json", 'r') as f:
        rx_config = json.load(f)

    # print(rx_config)
    sa_data = {
        'testing_duration': 60,
        'json_config': rx_config,
    }
    res = conducted_signal_quality.run_sa(sa_data)
    print("结果：" + res)

    # res = c.run_sg(10)
    # print(res)
