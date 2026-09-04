from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_exceptions_module_compiles():
    path = ROOT / "instrument_queue_dev" / "exceptions" / "exceptions.py"
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
