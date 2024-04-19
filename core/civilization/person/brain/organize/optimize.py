import re
from typing import List, Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action import ActionType
from core.civilization.person.action.base import Plan

from .base import BaseOrganize, Decision

_TEMPLATE = """
## Background
The type of action you can take is:
{action_types}

Your experts:{experts}
Your tools:{tools}

==========desired format==========
[Accept] or [Reject] your opinion
==========response example==========
[Reject] Actually, I think that the plan is not good.
Because it is not efficient.
========================================

Check your affordance of plan on request. Request is:
{request}

You must not remake plan, just say opinion to increase affordance plan. Opinion is harsh, but it is the best way to increase affordance of plan.
If you Reject, you will tell which condition is not satisfied for request.
If you Accept, you will tell which condition is satisfied for request

You can consider following things.
- constraint: constraints must be satisfied with plan. ex) tools are in path tools/, code is in path playground/, etc.
- tool: you can only use tool once per action of plan. ex) you can't use code_writer to write html and js and python code in one action

Every plan must be written up in a single line.
Your plans are:
{plans}

Check and increase affordance of your plan on request.
"""

_PATTERN = rf"\[({Decision.ACCEPT.value}|{Decision.REJECT.value})\](.*)"


class Optimizer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, request: str, plans: List[Plan]) -> str:
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
                [type.__str__(1) for type in ActionType if type.description is not None]
            ),
            request=request,
            experts=experts,
            tools=tools,
            plans="\n".join(map(str, plans)),
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            return "Your response is not in the correct schema.", False

        match = matches[0]

        return match[1].strip(), Decision(match[0]) == Decision.ACCEPT
