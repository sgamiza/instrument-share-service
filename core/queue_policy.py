"""Per-instrument FIFO queues and MQTT-style wait timeout."""

from __future__ import annotations

from collections import defaultdict, deque
from queue import Empty, Queue
from typing import Any, Optional

from .dispatch import TaskRequest
from .exceptions import MsgReceived


class PerInstrumentScheduler:
    def __init__(self) -> None:
        self._queues: dict[str, deque[TaskRequest]] = defaultdict(deque)

    def submit(self, request: TaskRequest) -> None:
        self._queues[request.instrument_id].append(request)

    def next_job(self, instrument_id: str) -> Optional[TaskRequest]:
        q = self._queues.get(instrument_id)
        if not q:
            return None
        return q.popleft()

    def pending(self, instrument_id: str) -> int:
        return len(self._queues.get(instrument_id, ()))

    def instrument_ids(self) -> list[str]:
        return list(self._queues.keys())


def wait_for_result(result_queue: Queue, timeout: float) -> Any:
    try:
        return result_queue.get(timeout=timeout)
    except Empty as exc:
        raise MsgReceived("No Msg Received!") from exc
