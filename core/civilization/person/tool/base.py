import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

from core.civilization.god import System
from core.logging import ANSI, Color, Style


class BuildParams(BaseModel):
    code: str

    @staticmethod
    def from_str(content: str):
        match = re.search(r"```python(.*?)```", content, re.DOTALL)
        if not match:
            return BuildParams(code="")

        code = match.group(1).strip()
        return BuildParams(code=code)


class UseParams(BaseModel):
    input: str

    @staticmethod
    def from_str(content: str):
        return UseParams(input=content)


class ToolMessageFormat:
    @staticmethod
    def greeting(self) -> str:
        return (
            f"{self.name}'s result\n{System.PROMPT_SEPARATOR}\n"
            + f"You have built a tool named {self.name}. Test if you can use the tool well."
        )

    @staticmethod
    def to_format(self, result: str) -> str:
        return f"{self.name}'s result\n{System.PROMPT_SEPARATOR}\n{result}"


class BaseTool(ABC, ToolMessageFormat):
    def __init__(self, name: str, instruction: str):
        self.name = name
        self.instruction = instruction
        self.color = Color.rgb(g=0)

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )

    @abstractmethod
    def build(self, params: BuildParams):
        pass

    @abstractmethod
    def use(self, prompt: str, params: UseParams) -> str:
        pass
