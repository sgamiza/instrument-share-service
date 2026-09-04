import os
import sys

# for linux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import instrument_queue_dev


# TODO 删除 py文件
if __name__ == '__main__':
    server = "127.0.0.1"
    # server = "127.0.0.1"
    # SA读取时间比较长 res_waite_timeout
    # 隐式等待 -》 显示等待
    res = instrument_queue_dev.run_client(server_type="sa",
                                          server_addr=server,
                                          config_file="config_tx.json",
                                          res_waite_timeout=200,
                                          rf_switch_ip="127.0.0.1",
                                          # rf_switch_port=31,
                                          rf_switch_port=[31,],
                                          )

    print(res)

