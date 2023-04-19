from core.civilization.god.system import System

from .base import BaseMemory


class ShortTermMemory(BaseMemory):
    def __init__(self, name: str, instruction: str):
        super().__init__(
            name=name,
            instruction=instruction,
            storage=[
                {"role": "system", "content": f"Your name is {name}. {instruction}"}
            ],
            change_to_memory=lambda x: x,
        )

    def load(self, prompt: str) -> str:
        return self.storage + [{"role": "user", "content": prompt}]

    def save(self, prompt: str, thought: str) -> None:
        self.storage.append(
            {"role": "user", "content": self.remove_guide(prompt)},
        )
        self.storage.append({"role": "assistant", "content": thought})

    def remove_guide(self, content: str) -> str:
        return content.split(System.MESSAGE_SEPARATOR)[1]
