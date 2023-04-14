import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

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


class BaseTool(BaseModel, ABC, arbitrary_types_allowed=True):
    name: str
    instruction: str
    color: Color = Color.rgb(g=128)

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
