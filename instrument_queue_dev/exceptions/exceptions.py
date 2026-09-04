class NameLookupError(KeyError):
    """
    Raised when unrecognized name for threeding.
    """



# class AliasLookupErrorTest(KeyError):
#     """
#     Raised when a lookup store is asked to resolve an unrecognized alias.
#     """


class MsgReceived(RuntimeError):
    """
    Raised when received a timeout msg
    """



class InsrumentTypeNotFound(KeyError):
    """
    Raised when not sa or sg
    """



class DeviceControlFailed(RuntimeError):
    """
    Raised when rf switch  cao not be contrifd
    """



class DeviceHoldTimeIncorrect(ValueError):
    """
    Raised when rf switch  cao not be contrifd
    """

