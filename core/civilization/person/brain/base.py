from abc import ABC, abstractmethod
from typing import Generator, List

from pydantic import BaseModel

from .llm import BaseLLM


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None

    @abstractmethod
    def think(self, prompt: str) -> Generator[str, None, None]:
        pass
