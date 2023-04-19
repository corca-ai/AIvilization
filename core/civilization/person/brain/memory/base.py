from abc import ABC, abstractmethod
from typing import Any, Callable

from pydantic import BaseModel


class BaseMemory(BaseModel, ABC):
    name: str = None
    instruction: str = None
    storage: Any = None
    change_to_memory: Callable = None

    @abstractmethod
    def load(self, prompt: str) -> str:
        pass

    @abstractmethod
    def save(self, prompt: str, thought: str) -> None:
        pass
