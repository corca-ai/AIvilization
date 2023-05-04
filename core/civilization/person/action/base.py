from enum import Enum
from typing import List

from pydantic import BaseModel

from core.logging import ANSI, Color, Style


class ActionType(Enum):
    Respond = "Respond"
    Invite = "Invite"
    Talk = "Talk"
    Build = "Build"
    Use = "Use"

    def __str__(self):
        return ANSI((self.value.lower() + "s ").center(12)).to(
            Color.rgb(210, 210, 210), Style.italic(), Style.dim()
        )


class Action(BaseModel):
    type: ActionType
    name: str
    instruction: str
    extra: str

    def __str__(self):
        return (
            f"Type: {self.type.value}\n"
            f"Name: {self.name}\n"
            f"Instruction: {self.instruction}\n"
            f"Extra: {self.extra}\n"
        )


class Plan(BaseModel):
    plan_number: int
    action_type: ActionType
    objective: str
    preceding_plan_numbers: List[int]

    def __str__(self):
        preceding_plans = ", ".join([f"#{p_n}" for p_n in self.preceding_plan_numbers])
        if len(preceding_plans) == 0:
            preceding_plans = "N/A"
        return f"{self.plan_number}. {self.action_type.value}: {self.objective} <{preceding_plans}>"

    def __repr__(self):
        preceding_plans = ", ".join([f"#{p_n}" for p_n in self.preceding_plan_numbers])
        if len(preceding_plans) == 0:
            preceding_plans = "N/A"
        return (
            f"action type={self.action_type.value}, action objective={self.objective}"
        )
