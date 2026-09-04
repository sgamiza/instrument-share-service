

import os
from instrument_queue_dev import run_client


def run_client_sg(server_addr, config_dir, res_waite_timeout,rf_switch_ip, rf_switch_port,sg_testing_hold_time=60):

    config_file = os.path.join(config_dir, "config_rx.json")

    return run_client(server_type="sg", server_addr=server_addr, config_file=config_file,
                      res_waite_timeout=res_waite_timeout,rf_switch_ip=rf_switch_ip, rf_switch_port=rf_switch_port,
                      sg_testing_hold_time=sg_testing_hold_time)
         


def run_client_sa(server_addr, config_dir, res_waite_timeout,rf_switch_ip, rf_switch_port):

    config_file = os.path.join(config_dir, "config_tx.json")

    return run_client(server_type="sa", server_addr=server_addr, config_file=config_file,
                      res_waite_timeout=res_waite_timeout, rf_switch_ip=rf_switch_ip, rf_switch_port=rf_switch_port)



