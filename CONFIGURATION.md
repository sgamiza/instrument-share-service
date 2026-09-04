# Instrument Share Service configuration

Put real values in a local untracked file or environment variables. Do not commit them.

| Item | Meaning | Example |
|---|---|---|
| `INSTRUMENT_SHARE_HOST` | Queue / MQTT bind address | `127.0.0.1` |
| Queue port | multiprocessing Manager port | `5000` |
| `authkey` | Manager auth bytes | `YOUR_AUTHKEY` |
| `tester_config.analyzer.device_address` | Spectrum analyzer address | `127.0.0.1` |
| `wanted_signal_generator_1.device_address` | Signal generator address | `127.0.0.1` |
| `rf_switch_ip` | RF Switch address | `127.0.0.1` |
| MQTT broker | Mosquitto | `127.0.0.1:1883` |
| `LAB_RF_PACKAGE` | Optional root package for RF measurement backends | unset uses in-repo stubs |
| `LAB_ALIAS_PACKAGE` | Optional package for handler alias lookup | unset uses in-repo stubs |

Copy `examples/config_tx.example.json` / `config_rx.example.json` and edit a local copy.

You can also put `LAB_RF_PACKAGE` and `LAB_ALIAS_PACKAGE` in a gitignored `.env` at the repo root. `instrument_queue_dev/optional_lab.py` loads that file before importing backends.

Offline policy matches the lab runtime (`core/dispatch.py` / `core/queue_policy.py`):

- Request `type` may only be `sa` / `sg` / `simple_reserve`
- `sg` and `simple_reserve` require `testing_duration > 0`, otherwise the type is illegal
- The same `instrument_id` is FIFO-serial; queues for different instruments do not block each other
- A client MQTT wait timeout raises `MsgReceived`
