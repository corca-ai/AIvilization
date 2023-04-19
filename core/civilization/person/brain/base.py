from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from .llm import BaseLLM
from .memory import BaseMemory


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None
    memory: List[BaseMemory] = None
    # If much earlier,  much closer to LLM. load last and save first.

    @abstractmethod
    def think(self, prompt: str) -> str:
        pass

    @classmethod
    def use_memory(cls, func):
        def wrapper(self: BaseBrain, idea: str) -> str:
            decorated_idea = idea
            for m in self.memory:
                decorated_idea = m.load(decorated_idea)

            thought = func(self, decorated_idea)

            for m in self.memory[::-1]:
                m.save(idea, thought)

            return thought

        return wrapper
