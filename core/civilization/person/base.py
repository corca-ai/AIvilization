from typing import Optional

from pydantic import BaseModel

from core.civilization.god.system import System
from core.logging import ANSI, Color, Style, logger

from .action import Action, ActionType
from .brain import BaseBrain
from .organize import BaseOrganize
from .tool import BaseTool


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
            + ".\nI was invited from you."
        )

    def to_format(self, message: str) -> str:
        return (
            System.MESSAGE_SEPARATOR
            + "\n"
            + f"{self.name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + message
        )


class BasePerson(BaseModel, PersonMessageFormat):
    name: str
    instruction: str
    params: InviteParams
    referee: Optional["BasePerson"] = None
    color: Color = Color.rgb(g=255)
    tools: dict[str, BaseTool] = {}
    brain: BaseBrain = None
    friends: dict[str, "BasePerson"] = {}
    organize: BaseOrganize = None

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )

    class Config:
        arbitrary_types_allowed = True


class Log:
    def to_idea(log_level: str):
        def decorator(func):
            def wrapper(self, prompt: str):
                idea = func(self, prompt)
                try:
                    getattr(logger, log_level)(
                        ANSI("[idea] ").to(Color.rgb(0xF6, 0xBA, 0x6F))
                        + ANSI(idea).to(Style.dim())
                    )
                except KeyError as e:
                    logger.error("Failed to log to_idea: " + str(e))

                return idea

            return wrapper

        return decorator

    def think(log_level: str):
        def decorator(func):
            def wrapper(self, idea: str):
                thought = func(self, idea)
                try:
                    getattr(logger, log_level)(
                        ANSI("[thought] ").to(Color.rgb(0x6D, 0xA9, 0xE4))
                        + ANSI(thought).to(Style.dim())
                    )
                except KeyError as e:
                    logger.error("Failed to log think: " + str(e))

                return thought

            return wrapper

        return decorator

    def to_actions(log_level: str):
        def decorator(func):
            def wrapper(self, thought: str):
                actions = func(self, thought)
                try:
                    getattr(logger, log_level)(
                        ANSI("[actions] ").to(Color.rgb(0xAD, 0xE4, 0xDB))
                        + ANSI(", ".join([str(action.type) for action in actions])).to(
                            Style.dim()
                        )
                    )
                except KeyError as e:
                    logger.error("Failed to log to_actions: " + str(e))

                return actions

            return wrapper

        return decorator

    def respond(log_level: str):
        def decorator(func):
            def wrapper(
                self: "BasePerson",
                sender: "BasePerson",
                prompt: str,
                params: TalkParams,
            ):
                result: str = func(self, sender, prompt, params)

                try:
                    getattr(logger, log_level)(
                        str(self)
                        + str(ActionType.Respond)
                        + str(sender)
                        + " | "
                        + ANSI(result.split(System.PROMPT_SEPARATOR)[1].strip()).to(
                            Color.white()
                        )
                    )
                except KeyError as e:
                    logger.error("Failed to log respond: " + str(e))

                return result

            return wrapper

        return decorator

    def act(log_level: str):
        def get_target(self, type: ActionType, name: str):
            if type in [ActionType.Invite, ActionType.Talk]:
                return self.friends[name]
            elif type in [ActionType.Build, ActionType.Use]:
                return self.tools[name]

        def decorator(func):
            def wrapper(self, action: Action):
                def f(target):
                    return (
                        str(self)
                        + str(action.type)
                        + ANSI(str(target)).to(Color.green(), Style.bold())
                        + " | "
                        + ANSI(action.instruction).to(Color.white())
                        + "\n"
                        + ANSI(action.extra).to(Style.dim())
                    )

                if action.type in [ActionType.Talk, ActionType.Use]:
                    try:
                        getattr(logger, log_level)(
                            f(get_target(self, action.type, action.name))
                        )
                    except KeyError as e:
                        logger.error("Failed to log act: " + str(e))

                result = func(self, action)

                if action.type in [ActionType.Invite, ActionType.Build]:
                    try:
                        getattr(logger, log_level)(
                            f(get_target(self, action.type, action.name))
                        )
                    except KeyError as e:
                        logger.error("Failed to log act: " + str(e))

                return result

            return wrapper

        return decorator
