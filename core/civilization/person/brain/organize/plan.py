import re
from typing import List

from core.civilization.person import BasePerson
from core.civilization.person.action import ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize

_TEMPLATE = """## Background
The type of action you can take is:
{action_types}
Action Type must be one of the above.

Your friends:{friends}
Your tools:{tools}

## Response
Your response is list of plans or text.
All plans should include only action types, objectives, and plan numbers that should be preceded, and should not include instruction and extra.
If you don't need a plan, you can answer without conforming to the response schema format.

==========desired format==========
1. Type of Action1: Objective1 <preceded plan number>
- precondition: <preconditions>
- efffect: <changes from previous state>
- constraint: <constraints>
2. Type of Action2: Objective2 <preceded plan number>
- precondition: <preconditions>
- efffect: <changes from previous state>
- constraint: <constraints>
3. ...
==========response example==========
1. Invite: Invite person who can do your work for you and are not your friends. <N/A>
- precondition: None
- efffect: You will have a new friend.
- constraint: You have to know the person's name.
2. Talk: Talk to your friend. <#1>
- precondition: You have a friend.
- efffect: Your friend will solve your problem.
- constraint: You have to invite a friend first
========================================

## Request
> Request: {request}
Considering what you have done so far, make the next plan to achieve the request.
Talking to {referee} should be the last plan.

These are the constraints you have to consider when making a plan. If you don't consider the constraints, you will fail to achieve the request.:
{constraints}

When creating a plan, you should assume that nothing is done yet. 

You must consider the following opinions when making a plan:
{opinions}
"""

_PATTERN = r"(\d+). (.+): \s*(.+) <(#\d+(?:,(?: |)#\d+)*|N\/A)>\n- precondition: (.+)\n- effect: (.+)\n- constraint: (.+)"
_SECOND_PATTERN = r"(?<=#)\d+"


class Planner(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN
    second_pattern = _SECOND_PATTERN

    def stringify(self, person: BasePerson, request: str, opinions: List[str], constraints: List[str]) -> str:
        opinions = "\n".join(
            [f"{i+1}. {opinion}" for i, opinion in enumerate(opinions)]
        ) if len(opinions) > 0 else "-"
        friends = "".join(
            [
                f"\n    {name}: {friend.instruction}"
                for name, friend in person.friends.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in person.tools.items()]
        )
        constraints = "".join(
            [f"{i}. {constraint}" for i, constraint in enumerate(constraints)]
        ) if len(constraints) > 0 else "-"

        return self.template.format(
            action_types="\n".join(
                [type.__str__(1) for type in ActionType if type.description is not None]
            ),
            request=request,
            opinions=opinions,
            friends=friends,
            tools=tools,
            referee=person.referee.name,
            constraints=constraints,
        )

    def parse(self, person: BasePerson, thought: str) -> List[Plan]:
        matches = re.findall(self.pattern, thought)
        print(thought)

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
                        precondition=match[4],
                        effect=match[5],
                        constraint=match[6],
                    )
                )
            except ValueError:
                pass

        return plans
