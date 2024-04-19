from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.person.action import Action, ActionType, Plan

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams


class BasePersonTracer:
    person: BasePerson

    def __init__(self, person: BasePerson):
        self.person = person

    def get_target(self, action: Action):
        target = None
        if action.type in [ActionType.Invite, ActionType.Talk]:
            target = self.person.experts[action.name]
        elif action.type in [ActionType.Build, ActionType.Use]:
            target = self.person.tools[action.name]
        return target

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        pass

    def on_thought_start(self):
        pass

    def on_thought(self, thought: str):
        pass

    def on_thought_end(self):
        pass

    def on_thought_error(self, error: Exception):
        pass

    def on_plans(self, plan: list[Plan]):
        pass

    def on_optimize(self, opinion: str, ok: bool):
        pass

    def on_act(self, action: Action):
        pass

    def on_act_error(self, action: Action, error: Exception):
        pass

    def on_act_result(self, action: Action, result: str):
        pass

    def on_review(self, opinion: str, ok: bool):
        pass

    def on_response(self, sender: BasePerson, response: str):
        pass

    def on_response_error(self, sender: BasePerson, error: Exception):
        pass
