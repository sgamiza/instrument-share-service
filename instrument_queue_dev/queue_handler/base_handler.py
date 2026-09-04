from functools import wraps
from contextlib import contextmanager

from instrument_queue_dev.optional_lab import aliasing_scope

from .queue_handler import QueueHandler

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class BaseHandler(object):
    # 父类、基本使用方法
    lookup_handler, store = aliasing_scope('handler', QueueHandler, name=__name__)

    def _extract_context_from_legncy(func):
        # print("debug _extract_context_from_legacy")
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # print(__name__," ",kwargs)
            if "instrument_id" in dict(kwargs):
                kwargs["handler"] = kwargs["instrument_id"]
                kwargs.pop("instrument_id")
            else:
                # 删除 ？
                for index, arg in enumerate(list(args)):  # 20220802 legacy bug: index, arg order was reversed
                    if isinstance(arg, QueueHandler):
                        kwargs["handler"] = arg  # kwargs 增加
                        # print("debug2", kwargs)
                        # args.pop(index)   # 20220802 legacy bug: 'tuple' object has no attribute 'pop'
                        args = self.del_tuple(index, args)  # fix bug
            # print("debug3",kwargs)

            return func(self, *args, **kwargs)

        return wrapper

    def del_tuple(self, index, args_tuple):
        if len(args_tuple) < 2:
            return tuple()
        return args_tuple[:index] + args_tuple[index + 1:]

    # @_extract_context_from_legncy
    # @lookup_handler.implicit_lookup
    # def activate_plan(self, timeout=10, handler=None):
    #     # 【下面函数修改】会导致如下错误：TypeError: no 'connection' argument found in 'activate_plan' signature.
    #     # def activate_plan(self):
    #     print(__name__, "activate_plan： ", handler)

    # @classmethod
    # @contextmanager
    # def admin_context(cls, **kwargs):
    #     """
    #     Context manager intended to simplify setting up
    #     and tearing down Admin by Python scripts.
    #     Performs setup at enter, frees resources at exit.
    #     Takes optional arguments passed to setup_admin.
    #     Examples available in the example folder
    #     """
    #     if "alias" in dict(kwargs):
    #         kwargs["connection"] = kwargs["alias"]
    #         kwargs.pop("alias")
    #
    #     admin_connection = None
    #     alias = kwargs.get("connection", "default")
    #     try:
    #         admin_connection = cls().connect_to(**kwargs)
    #         yield admin_connection
    #     finally:
    #         if admin_connection is not None:
    #             cls.store.remove(alias)
    #             admin_connection.disconnect()

    @_extract_context_from_legncy
    @lookup_handler.implicit_lookup
    def dispatch_queue(self, task_lock_request,
                       handler: QueueHandler = None):
        # handler.dispatch(task_lock_request)
        handler.add_to_queue(task_lock_request)



# TODO 删除 __main__
if __name__ == '__main__':
    # AliasLookupError: 'Default alias used, but no object set as default.'
    t = BaseHandler()
    t.activate_plan()  # : 'Default alias used, but no object set as default.'
