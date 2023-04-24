from abc import ABC, abstractmethod
from typing import Generator

from pydantic import BaseModel

from core.civilization.person.brain.organize.base import BaseOrganize

from .llm import BaseLLM


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None

    @abstractmethod
    def plan(self, prompt: str) -> str:
        pass

    @abstractmethod
    def execute(self, prompt: str) -> str:
        pass

    @abstractmethod
    def optimize(self, prompt: str) -> str:
        pass

    @abstractmethod
    def review(self, prompt: str) -> str:
        pass
