import abc


class ProtocolBase(metaclass=abc.ABCMeta):
    
    @classmethod
    def __subclasshook__(cls, subclass):
        pass

    @abc.abstractmethod
    def get_bytes(self) -> bytes:
        """Returns protocol dumped to bytes"""
        raise NotImplementedError

    