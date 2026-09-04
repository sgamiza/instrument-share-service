import os
import sys

# for linux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import instrument_queue_dev


# TODO 删除 py文件
if __name__ == '__main__':
    server = "127.0.0.1"

    import time
    # 申请 instrument_id123 60s 使用时间
    print("开始申请设备：",time.strftime("%Y_%m_%d %H:%M_%S"))
    # 连接设备需要5s
    res = instrument_queue_dev.run_client_simple_reserve(server_addr=server,instrument_id="instrument_id123", res_waite_timeout=20, hold_time=60,)
    print(res)
    print("结束申请设备：",time.strftime("%Y_%m_%d %H:%M_%S"))

    if res:
        print("使用设备。。。")
        time.sleep(20)
        print("。。。使用设备")

    else:
        # 【bug】如果申请超时，那边其实已经放在队列了，暂时还没有处理了，处理的时候还需要加上hold_time，就会导致永远连接不上
        pass


    print("结束使用设备：",time.strftime("%Y_%m_%d %H:%M_%S"))



