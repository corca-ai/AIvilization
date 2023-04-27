from enum import Enum

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
            f"{self.type.value}\n"
            f"name: {self.name}\n"
            f"instruction: {self.instruction}\n"
            f"extra: {self.extra}\n"
        )


class Plan(BaseModel):
    action_type: ActionType
    objective: str

    def __str__(self):
        return f"{self.action_type.value}: {self.objective}"
