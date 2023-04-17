from abc import ABC, abstractmethod

from pydantic import BaseModel

from .llm import BaseLLM
from .memory import BaseMemory


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None
    ltm: BaseMemory = None  # Long term memory
    stm: list[dict] = []  # Short term memory

    @abstractmethod
    def think(self, prompt: str) -> str:
        pass
