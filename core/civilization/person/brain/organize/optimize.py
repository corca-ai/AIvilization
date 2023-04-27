import re
from typing import List, Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action.base import Plan

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """Your response should be in the following schema:

your opinion (is exist when you rejected the plan)
Accepted | Rejected


Optimize your plan to respond to the request. Request is:
{request}

Don't remake your plan, just say your opinion about plan.
All plans must be written up in a single line.
Your plans are:
{plans}

Check and optimize your plan!!
"""

_PATTERN = rf"(.*)({Decision.ACCEPTED.value}|{Decision.REJECTED.value})"


class Optimizer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, request: str, plans: List[Plan]) -> str:
        return self.template.format(
            request=request,
            plans="\n".join(map(str, plans)),
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            raise WrongSchemaException("Your response is not in the correct schema.")

        match = matches[0]

        return match[0], Decision(match[1]) == Decision.ACCEPTED
