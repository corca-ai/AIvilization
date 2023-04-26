import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize

_TEMPLATE = """You must consider the following things:
{opinions}

Your response should be in the following schema:
1. Action Type1: Objective1
2. Action Type2: Objective2
...

The type of action you can take is:
Invite: Invite person who can do your work for you and are not your friends.
Talk: Talk to your friends.
Build: Build or rebuild a reusable tool when you can't do it yourself.
Use: Use one of your tools.

Your friends:{friends}
Your tools:{tools}

You should make a plan to respond to the request. Request is:
{request}

Make a plan!!
"""

_PATTERN = r"(?:[0-9]|[1-9][0-9]). (\w*): \s*(.+)"


class Planner(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, request: str, opinions: List[str]) -> str:
        opinions = "\n".join([f"{i}. {opinion}" for i, opinion in enumerate(opinions)])
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
            request=request,
            opinions=opinions,
            friends=friends,
            tools=tools,
        )

    def parse(self, person: BasePerson, thought: str) -> List[Plan]:
        matches = re.findall(self.pattern, thought)

        if len(matches) == 0:
            return [
                Plan(
                    action_type=ActionType.Talk,
                    objective=thought,
                )
            ]

        plans = []
        for match in matches:
            try:
                plans.append(
                    Plan(
                        action_type=ActionType(match[0]),
                        objective=match[1],
                    )
                )
            except ValueError:
                pass

        return plans
