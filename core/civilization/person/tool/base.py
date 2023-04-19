import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

from core.civilization.god.system import System
from core.logging import ANSI, Color, Style


class BuildParams(BaseModel):
    code: str

    @staticmethod
    def from_str(content: str):
        match = re.search(r"```(.*?)\n(.*?)```", content, re.DOTALL)
        if not match:
            return BuildParams(code="")

        code = match.group(2).strip()
        return BuildParams(code=code)


class UseParams(BaseModel):
    input: str

    @staticmethod
    def from_str(content: str):
        return UseParams(input=content)


class ToolMessageFormat:
    def greeting(self) -> str:
        return (
            f"{System.MESSAGE_SEPARATOR}\n"
            f"{self.name}'s result\n{System.PROMPT_SEPARATOR}\n"
            f"You have built a tool named {self.name}."
            "Test if you can use the tool well."
        )

    def to_format(self, result: str) -> str:
        return (
            f"{System.MESSAGE_SEPARATOR}\n"
            f"{self.name}'s result\n{System.PROMPT_SEPARATOR}\n{result}\n\n"
            "Look at the tool's response and think about what action you should take."
        )


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
