from enum import Enum
from typing import List

from pydantic import BaseModel

from core.logging import ANSI, Color, Style


class ActionProperty(BaseModel):
    description: str
    name: str
    instruction: str
    extra: str


class ActionType(Enum):
    Respond = "Respond"
    Invite = (
        "Invite",
        ActionProperty(
            description=(
                "Invite experts, when you want to discuss it with someone else"
            ),
            name="general person name like John, Steve",
            instruction="Personality",
            extra="one of tools among {tool_names} that the person needs.",
        ),
    )
    Talk = (
        "Talk",
        ActionProperty(
            description="Talk to your friends.",
            name="Friend's Name (should be one of {friend_names})",
            instruction="Message",
            extra="Attachment File List",
        ),
    )
    Build = (
        "Build",
        # ActionProperty(
        #     description=(
        #         "Build or rebuild a reusable tool when you can't do it yourself. "
        #         "It must have stdout, stderr messages. "
        #         "It should be executable with the following schema of commands: `python tools/example.py instruction extra`"
        #     ),
        #     name="Tool's Name (snake_case)",
        #     instruction="Tool's description that includes objective, instruction format, extra format, output format",
        #     extra='Python Code for Building Tools (format: ```pythonprint("hello world")```)',
        # ),
    )
    Use = (
        "Use",
        ActionProperty(
            description="Use one of your tools.",
            name="Tool's Name (should be one of {tool_names})",
            instruction="Input for using the tool. Refer to the guide of the tool you want to use.",
            extra="Extra Input for using the tool. Refer to the guide of the tool you want to use.",
        ),
    )

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, action_property: ActionProperty = None):
        self._description_ = action_property.description if action_property else None
        self._name_ = action_property.name if action_property else None
        self._instruction_ = action_property.instruction if action_property else None
        self._extra_ = action_property.extra if action_property else None

    def __str__(self, verbose_level: int = 0):
        if verbose_level == 0:
            return ANSI((self.value.lower() + "s ").center(12)).to(
                Color.rgb(210, 210, 210), Style.italic(), Style.dim()
            )
        elif verbose_level == 1:
            return self.value + " | " + self.description
        elif verbose_level == 2:
            return (
                f"{self.value} | "
                f"{self.description} | "
                f"{self.name} | "
                f"{self.instruction} | "
                f"{self.extra}"
            )

    @property
    def description(self):
        return self._description_

    @property
    def name(self):
        return self._name_

    @property
    def instruction(self):
        return self._instruction_

    @property
    def extra(self):
        return self._extra_


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
    precondition: str
    constraint: str
    effect: str

    def __str__(self):
        preceding_plans = ", ".join([f"#{p_n}" for p_n in self.preceding_plan_numbers])
        if len(preceding_plans) == 0:
            preceding_plans = "N/A"
        return f"{self.plan_number}. {self.action_type.value}: {self.objective} <{preceding_plans}>\n- precondition: {self.precondition}\n- effect: {self.effect}\n- constraint: {self.constraint}"

    def __repr__(self):
        preceding_plans = ", ".join([f"#{p_n}" for p_n in self.preceding_plan_numbers])
        if len(preceding_plans) == 0:
            preceding_plans = "N/A"
        return (
            f"action type={self.action_type.value}, action objective={self.objective}, action precondition={self.precondition}, action effect={self.effect}, action constraint={self.constraint}"
        )
