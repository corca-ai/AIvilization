from abc import ABC, abstractmethod
from typing import Generator, List

from pydantic import BaseModel

from .llm import BaseLLM
from .memory import BaseMemory


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None
    memory: List[BaseMemory] = None
    # If much earlier,  much further to LLM. load last and save first.

    @abstractmethod
    def think(self, prompt: str) -> Generator:
        pass

    @classmethod
    def use_memory(cls, func):
        def wrapper(self: BaseBrain, idea: str) -> str:
            decorated_idea = idea
            for m in self.memory[::-1]:
                decorated_idea = m.load(decorated_idea)

            thought = func(self, decorated_idea)

            for m in self.memory:
                m.save(idea, thought)

            return thought

        return wrapper
