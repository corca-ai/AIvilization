from abc import ABC, abstractmethod

from pydantic import BaseModel

from .llm import BaseLLM


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None
    stm: list[dict] = []

    @abstractmethod
    def think(self, prompt: str) -> str:
        pass
