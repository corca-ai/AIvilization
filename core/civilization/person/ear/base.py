from abc import ABC, abstractmethod
from enum import Enum
from socket import socket


class MessageType(Enum):
    Default = 1


class BaseEar(ABC):
    listener_socket: socket
    port: int

    def __init__(self):
        pass

    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def wait(self):
        pass
