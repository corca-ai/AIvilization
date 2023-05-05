from abc import ABC, abstractmethod
from enum import Enum
from socket import socket
from core.civilization.person.base import BasePerson


class MessageType(Enum):
    Default = 1


class BaseEar(ABC):
    listner_socket: socket
    person: BasePerson
    port: int

    def __init__(self):
        pass

    @abstractmethod
    async def listen(self):
        pass

    @abstractmethod
    def wait(self):
        pass
