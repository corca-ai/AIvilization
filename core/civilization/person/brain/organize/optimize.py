import re
from typing import List, Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action.base import Plan

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """
==========desired format==========
You must wrap your Accept/Reject with [].
[Accept/Reject]: Reason
==========response examples==========
[Accept]: The plan is well-structured, comprehensive, and addresses all key aspects of the project.
[Reject]: The plan does not provide a clear timeline or allocation of resources, making it difficult to assess its feasibility.
[Accept]: The plan demonstrates a thorough understanding of the problem and proposes innovative solutions to address it.
[Reject]: The plan relies on unrealistic assumptions and does not provide alternative strategies in case of setbacks.
========================================

Optimize your plan to respond to the request. Request is:
{request}

Don't remake your plan, just say your opinion about plan.
Every plan must be written up in a single line.
Your plans are:
{plans}

Check and optimize your plan!!
"""

_PATTERN = rf"\[({Decision.ACCEPT.value}|{Decision.REJECT.value})\](.*)"


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

        return match[1].strip(), Decision(match[0]) == Decision.ACCEPT
