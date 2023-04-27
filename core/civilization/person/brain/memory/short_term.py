
from .base import BaseMemory


class ShortTermMemory(BaseMemory[list[dict[str, str]]]):
    def __init__(self, name: str, instruction: str, init_message: str):
        super().__init__(
            name=name,
            instruction=instruction,
            storage=[
                {
                    "role": "system",
                    "content": init_message.format(name=name, instruction=instruction),
                }
            ],
            change_to_memory=lambda x: x,
        )

    def load(self, prompt: str) -> list[dict[str, str]]:
        return self.storage + [{"role": "user", "content": prompt}]

    def save(self, prompt: str, thought: str) -> None:
        self.storage.append({"role": "user", "content": prompt})
        self.storage.append({"role": "assistant", "content": thought})
