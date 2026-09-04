"""Per-instrument alias store, matching InstrumentStore without six/abc boilerplate."""

from __future__ import annotations

from typing import Any

from .exceptions import NameLookupError


class InstrumentStore:
    def __init__(self, name: str | None = None) -> None:
        self._store: dict[str, Any] = {}
        self.name = name

    def __len__(self) -> int:
        return len(self._store)

    def add(self, instance: Any, name: str) -> None:
        self._store[name] = instance

    def get(self, name: str) -> Any:
        if name not in self._store:
            raise NameLookupError(name)
        return self._store[name]

    def remove(self, name: str) -> None:
        instance = self.get(name)
        bound = [key for key, value in self._store.items() if value is instance]
        for key in bound:
            del self._store[key]

    def reset(self) -> None:
        self._store = {}

    @property
    def all(self):
        return self._store.items()
