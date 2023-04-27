import re
from typing import Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """Your response should be in the following schema:

your opinion (if you rejected the plan)
Accepted | Rejected


Review your execution result for executing "{plan}".
Your action is:
{action}

Your result of action is:
{result}

Don't execute again, just say your opinion about action and result.
Review your execution!!
"""

_PATTERN = rf"(.*)({Decision.ACCEPTED.value}|{Decision.REJECTED.value})"


class Reviewer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(
        self, person: BasePerson, plan: str, action: Action, result: str
    ) -> Tuple[str, bool]:

        return self.template.format(
            plan=plan,
            action=action,
            result=result,
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            raise WrongSchemaException("Your response is not in the correct schema.")

        match = matches[0]

        return match[0], Decision(match[1]) == Decision.ACCEPTED
