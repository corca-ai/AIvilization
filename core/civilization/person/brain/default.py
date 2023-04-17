from core.civilization.god.system import System

from .base import BaseBrain
from .llm.openai import OpenAILLM
from .memory.openai import OpenAIMemory


class Brain(BaseBrain):
    def __init__(self, name: str, instruction: str, memory: list[dict]):
        super().__init__(
            llm=OpenAILLM(),
            ltm=OpenAIMemory(),
            stm=[{"role": "system", "content": f"Your name is {name}. {instruction}"}]
            + (memory if memory else []),
        )

    def think(self, prompt: str) -> str:
        result = self.llm.chat_completion(
            self.stm + [{"role": "user", "content": prompt}]
        )
        self.stm.append(
            {"role": "user", "content": prompt.split(System.PROMPT_SEPARATOR)[1]}
        )
        self.stm.append({"role": "assistant", "content": result})
        return result
