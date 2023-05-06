from abc import ABC, abstractmethod
from typing import Dict, Generator, List

from pydantic import BaseModel


class BaseLLM(BaseModel, ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]]) -> Generator:
        pass
