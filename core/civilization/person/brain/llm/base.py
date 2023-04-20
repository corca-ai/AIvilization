from abc import ABC, abstractmethod
from typing import Generator

from pydantic import BaseModel


class BaseLLM(BaseModel, ABC):
    @abstractmethod
    def chat_completion(self, prompt: str) -> Generator:
        pass
