import instrument_queue_dev


# TODO 删除 py文件
if __name__ == '__main__':
    server = "127.0.0.1"
    # server = "127.0.0.1"
    # 显示等待 res_waite_timeout 120  -》 隐式等待
    # 仪表保持时间 sg_testing_hold_time 90
    res = instrument_queue_dev.run_client(server_type="sg",
                                          server_addr=server,
                                          config_file="config_rx.json",
                                          res_waite_timeout=120,
                                          rf_switch_ip="127.0.0.1",
                                          # 只能 rf switch
                                          # rf_switch_port=32,
                                          # tuple robot 不好写
                                          # rf_switch_port=(32,33),
                                          # list robot 好写
                                          # rf_switch_port=[32,33],
                                          rf_switch_port=[32,],
                                          sg_testing_hold_time=10)  # 操作rf switch比较花费时间

    print(res)


