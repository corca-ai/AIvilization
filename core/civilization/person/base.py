from typing import Optional

from pydantic import BaseModel

from core.logging import ANSI, Color, Style, logger

from .action import Action, ActionType
from .brain import BaseBrain
from .organize import BaseOrganize
from .tool import BaseTool


class CreateParams(BaseModel):
    tools: dict
    # channels: list[str] # TODO

    @staticmethod
    def from_str(content: str):
        return CreateParams(tools={})


class TalkParams(BaseModel):
    attachment: list[str]

    @staticmethod
    def from_str(content: str):
        return TalkParams(attachment=[])


class BasePerson(BaseModel):
    name: str
    instruction: str
    params: CreateParams
    referee: Optional["BasePerson"] = None
    color: Color = Color.rgb(r=128)
    memory: list = []
    tools: dict[str, BaseTool] = {}
    brain: BaseBrain = None
    friends: dict[str, "BasePerson"] = {}
    organize: BaseOrganize = None

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )


class Log:
    def organize(log_level: str):
        def decorator(func):
            def wrapper(self, prompt: str):
                idea = func(self, prompt)
                try:
                    getattr(logger, log_level)(ANSI(idea).to(Color.rgb(144, 144, 144)))
                except KeyError as e:
                    logger.error("Failed to log organize: " + str(e))

                return idea

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
                result = func(self, sender, prompt, params)

                try:
                    getattr(logger, log_level)(
                        str(self)
                        + str(ActionType.Respond)
                        + str(sender)
                        + " | "
                        + ANSI(result).to(Color.white())
                    )
                except KeyError as e:
                    logger.error("Failed to log respond: " + str(e))

                return result

            return wrapper

        return decorator

    def act(log_level: str):
        def get_target(self, type: ActionType, name: str):
            if type in [ActionType.Create, ActionType.Talk]:
                return self.friends[name]
            elif type in [ActionType.Build, ActionType.Use]:
                return self.tools[name]

        def decorator(func):
            def wrapper(self, action: Action):
                f = lambda target: (
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

                if action.type in [ActionType.Create, ActionType.Build]:
                    try:
                        getattr(logger, log_level)(
                            f(get_target(self, action.type, action.name))
                        )
                    except KeyError as e:
                        logger.error("Failed to log act: " + str(e))

                return result

            return wrapper

        return decorator

    def parse_thought(log_level: str):
        def decorator(func):
            def wrapper(thought: str):
                try:
                    getattr(logger, log_level)(
                        ANSI(thought).to(Color.rgb(208, 208, 208))
                    )
                except KeyError as e:
                    logger.error("Failed to log parse_thought: " + str(e))

                return func(thought)

            return wrapper

        return decorator
