import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize

_TEMPLATE = """You must consider the following things:
{opinions}

==========your response schema==========
1. Action Type1: Objective1 <Preceding plan number>
2. Action Type2: Objective2 <Preceding plan number>
3. ...
==========  response example  ==========
1. Invite: Invite person who can do your work for you and are not your friends. <N/A>
2. Talk: Talk to your friends. <#1>
========================================
If you don't need a plan, you can answer without conforming to the response schema format.

The type of action you can take is:
Invite: Invite experts who can do the things you don't know how to do for you.
Talk: Talk to your friends.
Build: Build or rebuild a reusable tool when you can't do it yourself.
Use: Use one of your tools.

Your friends:{friends} 
Your tools:{tools}

Your last plan should be talking to {referee}.
You should make a plan to respond to the request. Plan has only a action type, objective, and preceding plan number.
Request is:
{request}

Make a plan!!
"""

_PATTERN = r"(\d+). (\w*): \s*(.+) <(#\d+(?:,(?: |)#\d+)*|N\/A)>"
_SECOND_PATTERN = r"(?<=#)\d+"


class Planner(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN
    second_pattern = _SECOND_PATTERN

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
            referee=person.referee.name,
        )

    def parse(self, person: BasePerson, thought: str) -> List[Plan]:
        matches = re.findall(self.pattern, thought)

        if len(matches) == 0:
            return [
                Plan(
                    plan_number=1,
                    action_type=ActionType.Talk,
                    objective=thought,
                    preceding_plan_numbers=[],
                )
            ]

        plans = []
        for match in matches:
            try:
                plans.append(
                    Plan(
                        plan_number=int(match[0]),
                        action_type=ActionType(match[1]),
                        objective=match[2],
                        preceding_plan_numbers=[
                            int(p_n)
                            for p_n in re.findall(self.second_pattern, match[3])
                        ],
                    )
                )
            except ValueError:
                pass

        return plans
