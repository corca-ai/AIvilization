from abc import ABC, abstractmethod
from typing import List, Tuple

from pydantic import BaseModel

from core.civilization.person.action.base import Plan

from .llm import BaseLLM


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None

    @abstractmethod
    def plan(self, request: str, opinion: str, constraints: List[str]) -> List[Plan]:
        pass

    @abstractmethod
    def optimize(self, request: str, plans: List[Plan]) -> Tuple[str, bool]:
        pass

    @abstractmethod
    def execute(self, plan: List[Plan]) -> str:
        pass

    @abstractmethod
    def review(self, prompt: str) -> Tuple[str, bool]:
        pass
