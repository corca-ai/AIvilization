from abc import ABC, abstractmethod
from core.civilization.person.ear import BaseEar


class BaseMouth(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def talk(self, to: BaseEar, instruction: str, extra: str):
        pass
