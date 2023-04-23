from typing import Generator

from .base import BaseBrain
from .llm.openai import OpenAILLM
from .memory import BaseMemory, LongTermMemory, ShortTermMemory


class Brain(BaseBrain):
    sterm_memory: BaseMemory[list[dict[str, str]]] = None
    lterm_memory: BaseMemory[str] = None

    def __init__(self, name: str, instruction: str):
        super().__init__(llm=OpenAILLM())
        self.lterm_memory = LongTermMemory(name, instruction)
        self.sterm_memory = ShortTermMemory(name, instruction)
        self.sterm_memory.storage.append(
            {
                "role": "system",
                "content": f"Your name is {name}. {instruction}",
            }
        )

    def think(self, idea: str) -> Generator[str, None, None]:
        decorated_idea = self.sterm_memory.load(idea)

        for thought in self.llm.chat_completion(decorated_idea):
            yield thought["choices"][0]["delta"].get("content", "")

    def memo(self, plan: list[str]) -> str:
        pass
