# Instrument Share Service

## Project overview and purpose

Share RF instruments (spectrum analyzers and signal generators) over a client/server queue instead of exclusive local lock. Clients submit JSON jobs; the server creates a FIFO queue per instrument address and runs jobs serially; MQTT delivers results asynchronously. Clients do not need instrument drivers and can be called from Robot Framework.

`core/` is the offline-testable business layer: JSONObject, alias-keyed Store, SA/SG/simple_reserve dispatch, FIFO queues, and MQTT wait timeouts. `instrument_queue_dev/` is the lab runtime (PyVISA / Mosquitto / RF Switch). Optional site-specific RF backends are loaded through environment variables; see CONFIGURATION.md.

## Feature list

- Client JSON requests; the server returns status codes
- Independent queues created dynamically per instrument `device_address`; multi-client requests are serialized
- MQTT subscription receipts and asynchronous result notification, with a unified timeout
- multiprocessing Manager queues plus a threading scheduler
- Instrument operations stay on the server; supports queue timeouts and SG occupancy hold time
- RF Switch / PA port control adapters
- Robot glue: `run_client_sa` / `run_client_sg`
- Fault isolation: a single failure does not hang the whole service
- pytest coverage for JSONObject, Store, dispatch policy, FIFO, and timeouts (no instruments)

## Tech stack and dependencies

- Python 3.8+
- Lab runtime: paho-mqtt, func-timeout; optional PyVISA and a site RF library
- Unit tests: pytest, pytest-cov (stdlib only)
- MQTT broker: Mosquitto

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## How to run and use

1. Start Mosquitto locally.
2. Copy the example config and fill instrument addresses via environment variables or a local untracked file.
3. Server:

```bash
set INSTRUMENT_SHARE_HOST=127.0.0.1
python -c "import instrument_queue_dev; instrument_queue_dev.run_server_linux('127.0.0.1')"
```

4. Client examples are in `examples/` and `robot/instrument_queue_robot_interface.py`.

Unit tests (no instruments / no broker):

```bash
python -m pytest -v --cov=core --cov-report=term-missing
```

## Project file structure

```text
.
├── README.md
├── CONFIGURATION.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .github/workflows/ci.yml
├── examples/
├── robot/
├── core/                         # offline-testable
│   ├── json_object.py
│   ├── instrument_store.py
│   ├── dispatch.py
│   ├── queue_policy.py
│   └── exceptions.py
├── instrument_queue_dev/
└── tests/
```
