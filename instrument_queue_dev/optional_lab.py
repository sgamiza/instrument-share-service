"""Optional lab backends loaded from environment variables.

Set these if you have a site-specific RF library:

- LAB_RF_PACKAGE: root package that exposes ``.interface``,
  ``.instrument_control.signal_generator_manager``, and ``.definitions.models``
- LAB_ALIAS_PACKAGE: package that exposes ``LookupHandler``, ``aliasing_scope``,
  and ``exceptions.AliasLookupError``

A gitignored ``.env`` or ``.env.local`` in the repo root is loaded first.
When unset, in-repo stubs keep the queue importable.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import Any


def _load_dotenv() -> None:
    root = Path(__file__).resolve().parents[1]
    for name in (".env", ".env.local"):
        path = root / name
        if not path.is_file():
            continue
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


class AliasLookupError(LookupError):
    pass


class _AliasExceptions:
    AliasLookupError = AliasLookupError


class _SimpleStore:
    def __init__(self, name: str | None = None) -> None:
        self._store: dict[str, Any] = {}
        self.name = name

    def add(self, instance: Any, name: str) -> None:
        self._store[name] = instance

    def get(self, name: str) -> Any:
        if name not in self._store:
            raise AliasLookupError(name)
        return self._store[name]

    def remove(self, name: str) -> None:
        instance = self.get(name)
        bound = [key for key, value in self._store.items() if value is instance]
        for key in bound:
            del self._store[key]


def _load_module(dotted: str):
    return importlib.import_module(dotted)


def _env_pkg(key: str) -> str | None:
    value = os.environ.get(key, "").strip()
    return value or None


class ConductedRfCommonMeasurement:
    """No-op base when LAB_RF_PACKAGE is not set."""


class SignalGeneratorManager:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Set LAB_RF_PACKAGE to use a signal generator backend.")


class ConductedRfCase:
    pass


class CarriersConfig:
    pass


class RxTesterConfig:
    pass


class SensitivityResult:
    pass


class _LookupHandlerHelper:
    def __init__(self, kind: str, cls: type) -> None:
        self.kind = kind
        self.cls = cls
        self.store = None

    def implicit_lookup(self, func):  # noqa: ANN001
        return func


def LookupHandler(kind: str, cls: type) -> _LookupHandlerHelper:
    return _LookupHandlerHelper(kind, cls)


def aliasing_scope(kind: str, cls: type, name: str | None = None, **kwargs: Any):
    handler = LookupHandler(kind, cls)
    store = _SimpleStore(name=name)
    return handler, store


exceptions = _AliasExceptions

_rf = _env_pkg("LAB_RF_PACKAGE")
if _rf:
    ConductedRfCommonMeasurement = getattr(
        _load_module(f"{_rf}.interface"), "ConductedRfCommonMeasurement"
    )
    SignalGeneratorManager = getattr(
        _load_module(f"{_rf}.instrument_control.signal_generator_manager"),
        "SignalGeneratorManager",
    )
    _models = _load_module(f"{_rf}.definitions.models")
    ConductedRfCase = getattr(_models, "ConductedRfCase")
    CarriersConfig = getattr(_models, "CarriersConfig")
    RxTesterConfig = getattr(_models, "RxTesterConfig")
    SensitivityResult = getattr(_models, "SensitivityResult")

_alias = _env_pkg("LAB_ALIAS_PACKAGE")
if _alias:
    _amod = _load_module(_alias)
    LookupHandler = getattr(_amod, "LookupHandler")
    aliasing_scope = getattr(_amod, "aliasing_scope")
    exceptions = getattr(_amod, "exceptions")
