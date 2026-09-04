
from pathlib import Path
from instrument_queue_dev.optional_lab import (
    CarriersConfig,
    ConductedRfCase,
    ConductedRfCommonMeasurement,
    RxTesterConfig,
    SignalGeneratorManager,
)

'''
rx_carriers_config = rx_config['carriers_config']
rx_tester_config = rx_config['tester_config']
# rx_tester_config['generator_combinations']['wanted_signal_generator_1']['calibration_data_file'] = os.path.join(tm_dir,"rx_inband_ws_antenna_port_1.cal")
sensitivity_config = rx_config['sensitivity_config']
uplink_analysis_config = rx_config['uplink_analysis_config']
'''


def run_rf_measurement_sg(rx_carriers_config, rx_tester_config, sensitivity_config, uplink_analysis_config):

    rf_measurement_rx = ConductedRfCommonMeasurement(carriers_config=rx_carriers_config,
                                                     log_root_path="logs",
                                                     debug=False)

    sensitivity_result = rf_measurement_rx.sensitivity(
        # 最新的版本需要修改成tester_config
        # test_config=rx_tester_config, # 老版本
        tester_config=rx_tester_config, # 新版本
        sensitivity_config=sensitivity_config,
        uplink_analysis_config=uplink_analysis_config,
        multi_carrier_mode=False
    )

    return sensitivity_result



def stop(rx_carriers_config, rx_tester_config, sensitivity_config, uplink_analysis_config):

    generator_manager = SignalGeneratorManager(
        rf_measurement_case=ConductedRfCase.Sensitivity,
        carriers_config=CarriersConfig(carriers=rx_carriers_config),
        tester_config=RxTesterConfig(tester_config=rx_tester_config),
        general_measurement_data_folder=Path('.')
    )
    generator_manager.ws_1.set_output_state(False)


def stop_sg(rx_config):

    rx_carriers_config = rx_config['carriers_config']
    rx_tester_config = rx_config['tester_config']
    # generator_manager = SignalGeneratorManager(
    #     rf_measurement_case=ConductedRfCase.Sensitivity,
    #     carriers_config=CarriersConfig(carriers=rx_carriers_config),
    #     tester_config=RxTesterConfig(tester_config=rx_tester_config),
    #     general_measurement_data_folder=Path('.')
    # )
    # generator_manager.ws_1.set_output_state(False)
    # import pprint
    # pprint.pprint(rx_carriers_config)
    # pprint.pprint(rx_tester_config)
    stop(rx_carriers_config, rx_tester_config, None, None)




