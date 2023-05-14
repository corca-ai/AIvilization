from __future__ import annotations

import json
from typing import TYPE_CHECKING

import redis

from core.civilization.god.system import System
from core.civilization.person.action import Action, ActionType, Plan

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams

from core.config import settings

from .base import BasePersonTracer


class RedisTracer(BasePersonTracer):
    def __init__(self, person: BasePerson):
        super().__init__(person)
        self.thought = ""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0
        )
        self.key = f"person:{self.person.name}"
        self.redis.delete(self.key)

    def log(self, event: str, message: str, **kwargs):
        self.redis.rpush(
            self.key, json.dumps({"event": event, "message": message, **kwargs})
        )

    def log_action(self, action: Action):
        self.log(
            "action",
            action.type.value,
            instruction=action.instruction,
            target=self.get_target(action).name,
            extra=action.extra,
        )

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        pass

    def on_thought_start(self):
        self.thought = ""
        self.log("thought_start", "")

    def on_thought(self, thought: str):
        self.thought += thought

    def on_thought_end(self):
        self.log("thought_end", "")
        self.thought = ""

    def on_thought_error(self, error: Exception):
        self.log("thought_error", error)

    def on_plans(self, plans: list[Plan]):
        self.log(
            "plans",
            [
                f"{plan.plan_number}. {plan.action_type.value}: {plan.objective}"
                for plan in plans
            ],
        )

    def on_optimize(self, opinion: str, ok: bool):
        self.log("optimize", opinion, ok=ok)

    def on_act(self, action: Action):
        if action.type in [ActionType.Talk, ActionType.Use]:
            self.log_action(action)

    def on_act_error(self, action: Action, error: Exception):
        self.log("act_error", error)

    def on_act_result(self, action: Action, result: str):
        if action.type in [ActionType.Invite, ActionType.Build]:
            self.log_action(action)

        self.log("act_result", result)

    def on_review(self, opinion: str, ok: bool):
        self.log("optimize", opinion, ok=ok)

    def on_response(self, sender: BasePerson, response: str):
        self.log("response", response.split(System.PROMPT_SEPARATOR)[1].strip())

    def on_response_error(self, sender: BasePerson, error: Exception):
        self.log("response_error", error)
