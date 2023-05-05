import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize, WrongSchemaException

_TEMPLATE = """You must consider the following things:
{opinions}

You have to respond only one action and the action consists of type, name, description, and extra.

==========your response schema==========
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

The type of action you can take is:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
{action_types}

Your friends:{friends}
Your tools:{tools}

Your plan: {plan}
Execute only this plan!!
"""

_PATTERN = r"Type:\s*((?:\w| )+)\s+Name:\s*((?:\w| )+)\s+Instruction:\s*((?:(?!Extra:).)+)\s+Extra:\s*((?:(?!Type:).)*)\s*"


class Executor(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, plan: Plan, opinions: List[str]) -> str:
        opinions = "\n".join(
            [f"{i+1}. {opinion}" for i, opinion in enumerate(opinions)]
        )
        friend_names = ", ".join([f"'{name}'" for name in person.friends.keys()])
        tool_names = ", ".join([f"'{name}'" for name in person.tools.keys()])
        friends = "".join(
            [
                f"\n    {name}: {friend.instruction}"
                for name, friend in person.friends.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in person.tools.items()]
        )
        return self.template.format(
            action_types="\n".join(
                [type.__str__(2) for type in ActionType if type.description is not None]
            ),
            plan=repr(plan),
            opinions=opinions,
            friend_names=friend_names,
            tool_names=tool_names,
            friends=friends,
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
