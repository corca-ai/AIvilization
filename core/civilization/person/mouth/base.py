from abc import ABC, abstractmethod

# from core.civilization.person.base import BasePerson, MessageType


class BaseMouth(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def talk(self, to: int, instruction: str, extra: str):
        pass
