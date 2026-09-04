"""JSONObject compatible with instrument_queue_dev.storage.stores_interface."""

from __future__ import annotations

import json
from typing import Any


class JSONObject(dict):
    def __init__(self, *args, **kwargs):
        self.objects = {}
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.serialize()

    def __getitem__(self, object_name: str) -> Any:
        return self.objects[object_name]

    def get(self, k: str, d: Any = None) -> Any:
        """Production get(): falsy stored values fall back to default."""
        stored = self.objects.get(k)
        return stored if stored else d

    def serialize(self) -> str:
        return json.dumps([{k: v} for k, v in self.objects.items()], indent=4, separators=(",", ":"))

    def get_obj(self) -> list[dict]:
        return [{k: v} for k, v in self.objects.items()]

    def append_object(self, name: str, parameters: Any = None) -> None:
        self.objects[name] = parameters
