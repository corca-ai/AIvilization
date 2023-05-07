from enum import Enum
from typing import Optional, Type, Self

from pydantic import BaseModel

from core.civilization.god.system import System
from core.civilization.person.action.base import Action, ActionType
from core.logging import ANSI, Color, Style
from abc import ABC, abstractmethod

from .brain import BaseBrain
from .tool import BaseTool
from .tracer import BasePersonTracer, PersonTracerWrapper
from .ear import BaseEar
from .mouth import BaseMouth


class InviteParams(BaseModel):
    tools: dict[str, BaseTool]
    # channels: list[str] # TODO

    @staticmethod
    def from_str(content: str, tools: dict[str, BaseTool] = {}):
        given_tools = {}
        for tool in content.split(","):
            tool = tool.strip()
            if tool in tools.keys():
                given_tools[tool] = tools[tool]
        return InviteParams(tools=given_tools)

    class Config:
        arbitrary_types_allowed = True


class TalkParams(BaseModel):
    attachment: list[str]

    @staticmethod
    def from_str(content: str):
        return TalkParams(attachment=[])


class PersonMessageFormat:
    def greeting(self) -> str:
        return (
            System.MESSAGE_SEPARATOR
            + "\n"
            + f"{self.name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + "Hello, I am "
            + self.name
            + ".\nYou invited me."
        )

    def to_format(self, message: str) -> str:
        return (
            System.MESSAGE_SEPARATOR
            + "\n"
            + f"{self.name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + message
        )


class MessageType(Enum):
    Default = 1


INSTRUCTION_LENGTH_BYTES = 4
EXTRA_LENGTH_BYTES = 4
MESSAGE_SENDER_BYTES = 12
MESSAGE_TYPE_BYTES = 4


INVALID_MESSAGE_SENDER_ERROR_MESSAGE = "Invalid Message Sender"
INVALID_MESSAGE_TYPE_ERROR_MESSAGE = "Invalid Message Type"


class BasePerson(BaseModel, PersonMessageFormat, ABC):
    name: str
    instruction: str
    params: InviteParams
    color: Color
    referee: Optional["BasePerson"] = None
    tools: dict[str, BaseTool] = {}
    brain: BaseBrain = None
    friends: dict[str, "BasePerson"] = {}
    tracer: PersonTracerWrapper = None
    ear: BaseEar = None
    mouth: BaseMouth = None

    def __init__(self, **data):
        super().__init__(**data)
        self.set_tracers(tracers=[])

    def set_tracers(self, tracers: list[BasePersonTracer]):
        self.tracer = PersonTracerWrapper(person=self, tracers=tracers)

    def add_tracer(self, Tracer: Type[BasePersonTracer]):
        self.tracer.add(Tracer)

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )

    @abstractmethod
    def respond(self, sender: Self, request: str, params: TalkParams) -> str:
        pass

    class Config:
        arbitrary_types_allowed = True
