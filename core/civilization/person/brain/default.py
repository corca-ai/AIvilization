
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

    @BaseBrain.use_memory
    def think(self, idea: str) -> str:
        return self.llm.chat_completion(idea)

    def memo(self, plan: list[str]) -> str:
        pass
