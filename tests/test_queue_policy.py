from queue import Queue

import pytest

from core.dispatch import TaskRequest
from core.exceptions import MsgReceived
from core.queue_policy import PerInstrumentScheduler, wait_for_result


def _job(instrument_id: str, name: str) -> TaskRequest:
    return TaskRequest(
        instrument_id=instrument_id,
        instrument_type="sa",
        json_config={"name": name},
    )


def test_fifo_per_instrument_and_isolation():
    scheduler = PerInstrumentScheduler()
    scheduler.submit(_job("sa-1", "first"))
    scheduler.submit(_job("sa-1", "second"))
    scheduler.submit(_job("sg-1", "other"))

    assert scheduler.pending("sa-1") == 2
    first = scheduler.next_job("sa-1")
    second = scheduler.next_job("sa-1")
    other = scheduler.next_job("sg-1")
    assert first.json_config["name"] == "first"
    assert second.json_config["name"] == "second"
    assert other.json_config["name"] == "other"
    assert scheduler.next_job("sa-1") is None


def test_wait_timeout_raises_msg_received():
    q = Queue()
    with pytest.raises(MsgReceived):
        wait_for_result(q, timeout=0.01)


def test_wait_returns_payload():
    q = Queue()
    q.put({"STATUS": "OK"})
    assert wait_for_result(q, timeout=0.2) == {"STATUS": "OK"}
