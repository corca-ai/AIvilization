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
    def to_idea():
        def decorator(func):
            def wrapper(self, prompt: str):
                idea = func(self, prompt)
                self.tracer.on_idea(idea)
                return idea

            return wrapper

        return decorator

    def think():
        def decorator(func):
            def wrapper(self, idea: str):
                thought = func(self, idea)
                self.tracer.on_thought(thought)
                return thought

            return wrapper

        return decorator

    def to_actions():
        def decorator(func):
            def wrapper(self, thought: str):
                actions = func(self, thought)
                self.tracer.on_actions(actions)
                return actions

            return wrapper

        return decorator

    def respond():
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
                return result

            return wrapper

        return decorator

    def act():
        def decorator(func):
            def wrapper(self, action: Action):
                self.tracer.on_act(action)
                result = func(self, action)
                self.tracer.on_act_result(action, result)
                return result

            return wrapper

        return decorator


__all__ = ["BasePersonTracer", "Trace", "PersonTracerWrapper"]
