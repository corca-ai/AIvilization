from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.god.system import System
from core.civilization.person.action import Action, ActionType
from core.logging import ANSI, Color, Style, logger

from .base import BasePersonTracer
from .wrapper import PersonTracerWrapper

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams


class Trace:
    def to_idea(log_level: str):
        def decorator(func):
            def wrapper(self, prompt: str):
                idea = func(self, prompt)
                self.tracer.on_idea(idea)
                try:
                    getattr(logger, log_level)(
                        ANSI("[idea] ").to(Color.rgb(0xF6, 0xBA, 0x6F)) + idea
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
                self.tracer.on_thought(thought)
                try:
                    getattr(logger, log_level)(
                        ANSI("[thought] ").to(Color.rgb(0x6D, 0xA9, 0xE4)) + thought
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
                self.tracer.on_actions(actions)
                try:
                    getattr(logger, log_level)(
                        ANSI("[actions] ").to(Color.rgb(0xAD, 0xE4, 0xDB))
                        + ", ".join([str(action.type) for action in actions])
                    )
                except KeyError as e:
                    logger.error("Failed to log to_actions: " + str(e))

                return actions

            return wrapper

        return decorator

    def respond(log_level: str):
        def decorator(func):
            def wrapper(
                self: BasePerson,
                sender: BasePerson,
                prompt: str,
                params: TalkParams,
            ):
                self.tracer.on_request(sender, prompt, params)
                result: str = func(self, sender, prompt, params)
                self.tracer.on_response(sender, result)

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

                self.tracer.on_act(action)
                result = func(self, action)
                self.tracer.on_act_result(action, result)

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


__all__ = ["BasePersonTracer", "Trace", "PersonTracerWrapper"]
