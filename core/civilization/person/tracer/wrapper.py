from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.person.action import Action, Plan

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams

from .base import BasePersonTracer


class PersonTracerWrapper(BasePersonTracer):
    def __init__(self, person: BasePerson, tracers: list[type[BasePersonTracer]] = []):
        super().__init__(person)
        self.tracers: list[BasePersonTracer] = []
        for Tracer in tracers:
            self.add(Tracer)

    def add(self, Tracer: type[BasePersonTracer]):
        self.tracers.append(Tracer(person=self.person))

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        for tracer in self.tracers:
            tracer.on_request(sender, prompt, params)

    def on_thought_start(self):
        for tracer in self.tracers:
            tracer.on_thought_start()

    def on_thought(self, thought: str):
        for tracer in self.tracers:
            tracer.on_thought(thought)

    def on_thought_end(self):
        for tracer in self.tracers:
            tracer.on_thought_end()

    def on_thought_error(self, error: Exception):
        for tracer in self.tracers:
            tracer.on_thought_error(error)

    def on_plans(self, plans: list[Plan]):
        for tracer in self.tracers:
            tracer.on_plans(plans)

    def on_optimize(self, opinion: str, ok: bool):
        for tracer in self.tracers:
            tracer.on_optimize(opinion, ok)

    def on_act(self, action: Action):
        for tracer in self.tracers:
            tracer.on_act(action)

    def on_act_error(self, action: Action, error: Exception):
        for tracer in self.tracers:
            tracer.on_act_error(action, error)

    def on_act_result(self, action: Action, result: str):
        for tracer in self.tracers:
            tracer.on_act_result(action, result)

    def on_review(self, opinion: str, ok: bool):
        for tracer in self.tracers:
            tracer.on_review(opinion, ok)

    def on_response(self, sender: BasePerson, response: str):
        for tracer in self.tracers:
            tracer.on_response(sender, response)

    def on_response_error(self, sender: BasePerson, error: Exception):
        for tracer in self.tracers:
            tracer.on_response_error(sender, error)
