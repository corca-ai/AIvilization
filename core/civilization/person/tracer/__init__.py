from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.person.action import Action

from .base import BasePersonTracer
from .wrapper import PersonTracerWrapper

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams


class Trace:
    def to_idea():
        def decorator(func):
            def wrapper(self, prompt: str):
                try:
                    idea = func(self, prompt)
                except Exception as e:
                    self.tracer.on_idea_error(e)
                    return None

                self.tracer.on_idea(idea)
                return idea

            return wrapper

        return decorator

    def think():
        def decorator(func):
            def wrapper(self, idea: str):
                try:
                    thought = func(self, idea)
                except Exception as e:
                    self.tracer.on_thought_error(e)
                    return None

                self.tracer.on_thought(thought)
                return thought

            return wrapper

        return decorator

    def to_actions():
        def decorator(func):
            def wrapper(self, thought: str):
                try:
                    actions = func(self, thought)
                except Exception as e:
                    self.tracer.on_actions_error(e)
                    return None

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
                try:
                    result: str = func(self, sender, prompt, params)
                except Exception as e:
                    self.tracer.on_response_error(sender, e)
                    return None

                self.tracer.on_response(sender, result)
                return result

            return wrapper

        return decorator

    def act():
        def decorator(func):
            def wrapper(self, action: Action):
                self.tracer.on_act(action)
                try:
                    result = func(self, action)
                except Exception as e:
                    self.tracer.on_act_error(action, e)
                    return None

                self.tracer.on_act_result(action, result)
                return result

            return wrapper

        return decorator


__all__ = ["BasePersonTracer", "Trace", "PersonTracerWrapper"]
