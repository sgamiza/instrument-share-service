import json
from pathlib import Path

import pytest

from core.dispatch import device_address_from_config, parse_task_request
from core.exceptions import InsrumentTypeNotFound
from core.json_object import JSONObject

ROOT = Path(__file__).resolve().parents[1]


def _tx_config():
    return json.loads((ROOT / "examples" / "config_tx.example.json").read_text(encoding="utf-8"))


def _rx_config():
    return json.loads((ROOT / "examples" / "config_rx.example.json").read_text(encoding="utf-8"))


def test_parse_sa_request():
    payload = JSONObject()
    payload.append_object("type", "sa")
    payload.append_object("instrument_id", "127.0.0.1")
    payload.append_object("json_config", _tx_config())
    req = parse_task_request(payload)
    assert req.instrument_type == "sa"
    assert req.testing_duration == 0
    assert device_address_from_config(req.instrument_type, req.json_config) == "127.0.0.1"


def test_parse_sg_requires_hold_time():
    payload = JSONObject()
    payload.append_object("type", "sg")
    payload.append_object("instrument_id", "sg-1")
    payload.append_object("json_config", _rx_config())
    with pytest.raises(InsrumentTypeNotFound):
        parse_task_request(payload)

    payload.append_object("testing_duration", 60)
    req = parse_task_request(payload)
    assert req.testing_duration == 60
    assert device_address_from_config("sg", req.json_config) == "127.0.0.1"


def test_unknown_type_raises():
    payload = JSONObject()
    payload.append_object("type", "power_meter")
    payload.append_object("json_config", {})
    with pytest.raises(InsrumentTypeNotFound):
        parse_task_request(payload)


def test_example_configs_use_loopback():
    assert _tx_config()["tester_config"]["analyzer"]["device_address"] == "127.0.0.1"
    gen = _rx_config()["tester_config"]["generator_combinations"]["wanted_signal_generator_1"]
    assert gen["device_address"] == "127.0.0.1"
