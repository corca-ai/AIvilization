from typing import Generator

from .base import BaseBrain
from .llm.openai import OpenAILLM
from .memory import LongTermMemory, ShortTermMemory


class Brain(BaseBrain):
    def __init__(self, name: str, instruction: str):
        super().__init__(
            llm=OpenAILLM(),
            memory=[
                LongTermMemory(name, instruction),
                ShortTermMemory(name, instruction),
            ],
        )

    def think(self, idea: str) -> Generator:
        decorated_idea = idea
        for m in self.memory[::-1]:
            decorated_idea = m.load(decorated_idea)

        thought = self.llm.chat_completion(decorated_idea)
        # for m in self.memory:
        #     m.save(idea, thought)

        return thought

    def memo(self, plan: list[str]) -> str:
        pass
