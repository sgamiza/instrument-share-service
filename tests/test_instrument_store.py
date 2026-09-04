import pytest

from core.exceptions import NameLookupError
from core.instrument_store import InstrumentStore


def test_add_get_remove():
    store = InstrumentStore("handlers")
    store.add("handler-a", "127.0.0.1")
    assert len(store) == 1
    assert store.get("127.0.0.1") == "handler-a"
    store.remove("127.0.0.1")
    assert len(store) == 0


def test_missing_alias_raises():
    store = InstrumentStore()
    with pytest.raises(NameLookupError):
        store.get("missing")


def test_reset_clears_all():
    store = InstrumentStore()
    store.add(1, "a")
    store.add(2, "b")
    store.reset()
    assert len(store) == 0
