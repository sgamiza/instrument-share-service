"""Exceptions matching instrument_queue_dev.exceptions without lab imports."""


class NameLookupError(KeyError):
    """Raised when an instrument alias is missing."""


class MsgReceived(RuntimeError):
    """Raised when a timeout wait finishes without a payload."""


class InsrumentTypeNotFound(KeyError):
    """Raised when type is not sa / sg / simple_reserve. Name kept for compatibility."""


class DeviceControlFailed(RuntimeError):
    """Raised when RF switch control fails."""


class DeviceHoldTimeIncorrect(ValueError):
    """Raised when SG / simple_reserve hold time is invalid."""
