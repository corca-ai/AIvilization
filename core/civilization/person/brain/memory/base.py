from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseMemory(Generic[T], BaseModel, ABC):
    name: str = None
    instruction: str = None
    storage: Any = None
    change_to_memory: Callable = None

    @abstractmethod
    def load(self, prompt: str) -> T:
        pass

    @abstractmethod
    def save(self, prompt: str, thought: str) -> None:
        pass
