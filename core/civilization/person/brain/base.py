from abc import ABC, abstractmethod

import pinecone
from pydantic import BaseModel

from .llm import BaseLLM
from .vector import BaseVector


class BaseBrain(BaseModel, ABC):
    llm: BaseLLM = None
    vector: BaseVector = None
    stm: list[dict] = []  # Short term memory
    ltm: pinecone.Index = None  # Long term memory
    name: str = None
    instruction: str = None

    @abstractmethod
    def think(self, prompt: str) -> str:
        pass

    class Config:
        arbitrary_types_allowed = True
