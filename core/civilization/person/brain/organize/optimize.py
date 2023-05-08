import re
from typing import List, Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action.base import ActionType, Plan

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """## Background
The type of action you can take is:
{action_types}

Your friends:{friends}
Your tools:{tools}

<plan schema>
1. Type1: Objective1 <preceded plan number>
2. Type2: Objective2 <preceded plan number>

## Response
You need to decide whether it is Accept or Reject.
==========   response schema  ==========
[Accept] or [Reject] your opinion
==========  response example  ==========
[Reject] Actually, I think that the plan is not good.
Because it is not efficient.
========================================

## Request
> Request: {request}

Your plans are:
{plans}

Check the feasibility, detail, and suit the plan schema of the plans.
You must follow the response schema.
"""

_PATTERN = rf"\[({Decision.ACCEPT.value}|{Decision.REJECT.value})\](.*)"


class Optimizer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, request: str, plans: List[Plan]) -> str:
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
                [type.__str__(1) for type in ActionType if type.description is not None]
            ),
            request=request,
            friends=friends,
            tools=tools,
            plans="\n".join(map(str, plans)),
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            return "Your response is not in the correct schema.", False

        match = matches[0]

        return match[1].strip(), Decision(match[0]) == Decision.ACCEPT
