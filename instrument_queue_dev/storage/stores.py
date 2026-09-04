
import logging


# 使用工程目录，pycharm才不会报错
# from exceptions.exceptions import AliasLookupError
from instrument_queue_dev.exceptions.exceptions import NameLookupError
from abc import ABCMeta, abstractmethod
from six import with_metaclass


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# TODO Alias to name

class Store(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def add(self, instance, name):
        raise NotImplementedError

    @abstractmethod
    def get(self, name):
        raise NotImplementedError

    @abstractmethod
    def remove(self, name):
        raise NotImplementedError


    @abstractmethod
    def reset(self):
        pass  # reset function


class InstrumentStore(Store):

    # DEFAULT_ALIAS = 'default'

    def __init__(self, name=None):
        self._store = {}
        self.name = name
        # self._log_init()


    def __len__(self):
        return len(self._store)

    def __repr__(self):
        reprstr = (
            "<{name} {clsname} at {id}>"
            if self.name is not None else
            "<{clsname} at {id}>"
        )
        return reprstr.format(
            name=self.name, clsname=self.__class__.__name__, id=hex(id(self))
        )

    def add(self, instance, name):
        # self._log_add(instance, alias)
        # alias = self._get_default_if_needed(alias)
        self._store[name] = instance


    def get(self, name):
        instance = self._get(name)
        # self._log_get(instance, alias)
        return instance

    def _get(self, name):
        # alias = self._get_default_if_needed(alias)
        self.__exists(name)
        return self._store[name]


    @property
    def all(self):
        return self._store.items()

    # @classmethod
    # def _get_default_if_needed(cls, alias):
    #     return alias or cls.DEFAULT_ALIAS

    def __exists(self, name):
        if name not in self._store:
            # if alias == self.DEFAULT_ALIAS:
            #     raise NameLookupError
            raise NameLookupError
            # self._raise_unrecognized_alias(alias)

    # def _raise_no_default_set(self):
    #     logger.debug("Resolving default alias failed in {!r}.".format(self))
    #     raise NameLookupError(
    #         "Default alias used, but no object set as default."
    #     )

    # def _raise_unrecognized_alias(self, alias):
    #     logger.debug("Resolving alias failed in {!r}.".format(self))
    #     raise NameLookupError("Unrecognized alias: {!r}.".format(alias))


    def remove(self, name):
        instance = self._get(name)
        bound_names = self._find_all_names_of_instance(instance)
        for i in bound_names:
            del self._store[i]
        # self._log_removed_all_occurences(instance, bound_aliases)

    def _find_all_names_of_instance(self, instance):
        return [k for k, v in self._store.items() if v == instance]


    # def _log_removed_all_occurences(self, instance, aliases):
    #     aliases_list = ', '.join(repr(alias) for alias in aliases)
    #     msg = "Unbound {!r} from all its aliases in {!r}: {}."
    #     logger.debug(msg.format(instance, self, aliases_list))


    def reset(self):
        # self._log_reset()
        self.__init__()


    # def _log_init(self):
    #     logger.debug("Initialized store: {!r}.".format(self))

    # def _log_add(self, instance, alias):
    #     logger.debug(
    #         "Binding {!r} to alias {!r} in {!r}.".format(instance, alias, self)
    #     )

    # def _log_get(self, instance, alias):
    #     msg = "Resolved alias {!r} to {!r} from {!r}."
    #     logger.debug(msg.format(alias, instance, self))

    # def _log_reset(self):
    #     logger.debug("Resetting {!r}.".format(self))





