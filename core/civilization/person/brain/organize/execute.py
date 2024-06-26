import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize, WrongSchemaException

_TEMPLATE = """
You must respond only one action and the action consists of type, name, description, and extra.

==========desired format==========
You must adhere to a format that includes Type, Name, Instruction, and Extra.
If you don't have anything to write in Extra, don't erase Extra by writing a space after Extra.
Type: example type
Name: example name
Instruction: example instruction
Extra: example extra
==========  response example  ==========
Type: Invite
Name: John
Instruction: The best engineer in the infinite universe.
Extra: tool1, tool2, tool3
========================================

You must consider the following opinions before you execute the action.
opinions: {opinions}

The type of action you can take is:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
{action_types}

Your experts:{experts}
Your tools:{tools}

Your plan: {plan}

Make action based on opinions and your plan. Don't execute action you made.
"""

_PATTERN = r"Type:\s*((?:\w| )+)\s+Name:\s*((?:\w| )+)\s+Instruction:\s*((?:(?!Extra:).)+)\s+Extra:\s*((?:(?!Type:).)*)\s*"


class Executor(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, plan: Plan, opinions: List[str]) -> str:
        opinions = (
            "\n".join([f"{i+1}. {opinion}" for i, opinion in enumerate(opinions)])
            if len(opinions) > 0
            else "N/A"
        )

        expert_names = (
            ", ".join([f"'{name}'" for name in person.experts.keys()])
            if len(person.experts) > 0
            else "N/A"
        )
        tool_names = (
            ", ".join([f"'{name}'" for name in person.tools.keys()])
            if len(person.tools) > 0
            else "N/A"
        )
        experts = "".join(
            [
                f"\n    {name}: {expert.instruction}"
                for name, expert in person.experts.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.description}" for name, tool in person.tools.items()]
        )
        return self.template.format(
            action_types="\n".join(
                [type.__str__(2) for type in ActionType if type.description is not None]
            ),
            plan=repr(plan),
            opinions=opinions,
            expert_names=expert_names,
            tool_names=tool_names,
            experts=experts,
            tools=tools,
        )

    def parse(self, person: BasePerson, thought: str) -> Action:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            raise WrongSchemaException("Your response is not in the correct schema.")

        match = matches[0]

        return Action(
            type=ActionType[match[0]],
            name=match[1],
            instruction=match[2],
            extra=match[3],
        )
