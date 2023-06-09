from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseVector(BaseModel, ABC):
    @abstractmethod
    def embedding(self, prompt: str) -> str:
        pass
