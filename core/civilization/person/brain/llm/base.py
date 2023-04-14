from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseLLM(BaseModel, ABC):
    @abstractmethod
    def chat_completion(self, prompt: str) -> str:
        pass
