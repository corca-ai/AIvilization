from __future__ import annotations

from typing import TYPE_CHECKING, Type

from core.civilization.person.action import Action

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams

from .base import BasePersonTracer


class PersonTracerWrapper(BasePersonTracer):
    tracers: list[BasePersonTracer] = []

    def __init__(self, person: BasePerson, tracers: list[Type[BasePersonTracer]] = []):
        super().__init__(person)
        self.tracers = tracers

    def add(self, Tracer: Type[BasePersonTracer]):
        self.tracers.append(Tracer(person=self.person))

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        for tracer in self.tracers:
            tracer.on_request(sender, prompt, params)

    def on_idea(self, idea: str):
        for tracer in self.tracers:
            tracer.on_idea(idea)

    def on_thought(self, thought: str):
        for tracer in self.tracers:
            tracer.on_thought(thought)

    def on_actions(self, actions: list[Action]):
        for tracer in self.tracers:
            tracer.on_actions(actions)

    def on_act(self, action: Action):
        for tracer in self.tracers:
            tracer.on_act(action)

    def on_act_result(self, action: Action, result: str):
        for tracer in self.tracers:
            tracer.on_act_result(action, result)

    def on_response(self, sender: BasePerson, response: str):
        for tracer in self.tracers:
            tracer.on_response(sender, response)
