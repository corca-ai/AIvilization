import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize

_TEMPLATE = """You should make a plan to respond to the "{request}".

Consider the opinions below as you develop your plan.
>>> {opinion}

Your response should be in the following schema:
1. Action Type1: Objective1
2. Action Type2: Objective2
...

The action types you can use are:
Invite: Invite person who can do your work for you and are not your friends.
Talk: Talk to your friends.
Build: Build or rebuild a reusable tool when you can't do it yourself.
Use: Use one of your tools.

Your friends:{friends}
Your tools:{tools}

Make a plan!!
"""

_PATTERN = r"(\w):\s*((?:\w| )+)\s"


class Planner(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, request: str, opinion: str) -> str:
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
            opinion=opinion,
            friends=friends,
            tools=tools,
        )

    def parse(self, person: BasePerson, thought: str) -> List[Plan]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        return [
            Plan(
                type=ActionType(match[0]),
                objective=match[1],
            )
            for match in matches
        ]
