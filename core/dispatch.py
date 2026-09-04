"""Parse and route a lock request the same way QueueHandler._dispatch does."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from .exceptions import InsrumentTypeNotFound
from .json_object import JSONObject

ALLOWED_TYPES = ("sa", "sg", "simple_reserve")
DEFAULT_INSTRUMENT_HOLD_TIME = 0


@dataclass(frozen=True)
class TaskRequest:
    instrument_id: str
    instrument_type: str
    json_config: Mapping[str, Any]
    testing_duration: int = DEFAULT_INSTRUMENT_HOLD_TIME
    mqtt_msg_id: Optional[str] = None
    rf_switch_ip: Optional[str] = None
    rf_switch_port: Optional[tuple] = None

    @property
    def needs_rf_switch(self) -> bool:
        return self.instrument_type != "simple_reserve" and self.rf_switch_ip is not None


def parse_task_request(payload: JSONObject | Mapping[str, Any]) -> TaskRequest:
    getter = payload.get if hasattr(payload, "get") else lambda k, d=None: payload[k] if k in payload else d

    def require(key: str) -> Any:
        try:
            if isinstance(payload, JSONObject):
                return payload[key]
            return payload[key]
        except KeyError as exc:
            raise InsrumentTypeNotFound(key) from exc

    instrument_type = require("type")
    if instrument_type not in ALLOWED_TYPES:
        raise InsrumentTypeNotFound(instrument_type)

    hold = getter("testing_duration", DEFAULT_INSTRUMENT_HOLD_TIME)
    if hold is None:
        hold = DEFAULT_INSTRUMENT_HOLD_TIME
    if instrument_type in ("sg", "simple_reserve") and not hold:
        raise InsrumentTypeNotFound("sg/simple_reserve require testing_duration > 0")

    instrument_id = getter("instrument_id") or "unknown"
    mqtt_msg_id = getter("mqtt_msg_id") or instrument_id
    rf_port = getter("rf_switch_port")
    if isinstance(rf_port, list):
        rf_port = tuple(rf_port)

    return TaskRequest(
        instrument_id=str(instrument_id),
        instrument_type=str(instrument_type),
        json_config=require("json_config"),
        testing_duration=int(hold),
        mqtt_msg_id=str(mqtt_msg_id),
        rf_switch_ip=getter("rf_switch_ip"),
        rf_switch_port=rf_port,
    )


def device_address_from_config(instrument_type: str, json_config: Mapping[str, Any]) -> str:
    tester = json_config["tester_config"]
    if instrument_type == "sa":
        return tester["analyzer"]["device_address"]
    if instrument_type == "sg":
        return tester["generator_combinations"]["wanted_signal_generator_1"]["device_address"]
    raise InsrumentTypeNotFound(instrument_type)
