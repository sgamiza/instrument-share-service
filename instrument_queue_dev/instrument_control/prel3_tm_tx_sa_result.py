
import os
import json
from instrument_queue_dev.optional_lab import ConductedRfCommonMeasurement

'''    
carriers_config = config['carriers_config']
tester_config = config['tester_config']
tester_config['analyzer']['calibration_data_file']=os.path.join(tm_dir, "tx_inband_antenna_port_1.cal")
signal_quality_config = config['signal_quality_config']
'''


def run_rf_measurement_sa(tx_carriers_config, tx_tester_config, signal_quality_config):

    rf_measurement = ConductedRfCommonMeasurement(carriers_config=tx_carriers_config,
                                                  log_root_path="logs", debug=False)

    signal_quality_results = rf_measurement.signal_quality_measure(tester_config=tx_tester_config,
                                                                   signal_quality_config=signal_quality_config)

    return signal_quality_results[0].results.evm_256qam





def run(tm_dir):

    config_file = os.path.join(tm_dir, "config_tx.json")
    with open(config_file, 'r') as f:
        config = json.load(f)

    carriers_config = config['carriers_config']
    tester_config = config['tester_config']
    tester_config['analyzer']['calibration_data_file']=os.path.join(tm_dir, "tx_inband_antenna_port_1.cal")
    signal_quality_config = config['signal_quality_config']

    rf_measurement = ConductedRfCommonMeasurement(carriers_config=carriers_config,
                                                  log_root_path="logs", debug=False)
    signal_quality_results = rf_measurement.signal_quality_measure(tester_config=tester_config,
                                                                   signal_quality_config=signal_quality_config)
    aclr_results = rf_measurement.aclr_measure(tester_config=tester_config, csv_report=True)
    output_power_results = rf_measurement.output_power_measure(tester_config=tester_config)

    return signal_quality_results[0].results.dict(), aclr_results[0].dict(), output_power_results[0].dict()
