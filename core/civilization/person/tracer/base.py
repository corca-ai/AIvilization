from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.person.action import Action

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams


class BasePersonTracer:
    person: BasePerson

    def __init__(self, person: BasePerson):
        self.person = person

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        pass

    def on_idea(self, idea: str):
        pass

    def on_thought(self, thought: str):
        pass

    def on_actions(self, actions: list[Action]):
        pass

    def on_act(self, action: Action):
        pass

    def on_act_result(self, action: Action, result: str):
        pass

    def on_response(self, sender: BasePerson, response: str):
        pass
