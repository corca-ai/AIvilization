import re
from typing import Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """
## Background
The type of action you can take is:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
{action_types}

Your friends:{friends}
Your tools:{tools}

## Response
Your response is a review on the action whether it achieved a plan or not. Which means goal was achieved by a single action.
Review must be harsh and clear. If you Accept, you will tell which condition is satisfied and there are no more things to do to achieve a goal.
If you Reject, you will tell what condition is not satisfied and what should be done to achieve a goal. It will be a constraint for the next plans and actions. 

==========desired format==========
[Accept] or [Reject] review of a action whether achieved a plan or not.
==========response example 1==========
[Reject] "Code must be executed not just written."
==========response example 2==========
[Accept] Action seems valid to achieve a goal you made. Action achieves goal "run a code and get output hello world" by 1) executing `python playgrounds/example.py` and 2) printing "hello world".
========================================

## Request
Check your action was valid for achieving following goal. Don't execute again, just say your opinion about action and result.

Your goal:
{goal}

Your action is:
{action}
Result of your action is:
{result}
"""

_PATTERN = rf"\[({Decision.ACCEPT.value}|{Decision.REJECT.value})\](.*)"


class Reviewer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(
        self, person: BasePerson, plan: str, action: Action, result: str
    ) -> Tuple[str, bool]:
        friend_names = ", ".join([f"'{name}'" for name in person.friends.keys()])
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
            goal=plan,
            action=action,
            result=result,
            friend_names=friend_names,
            action_types="\n".join(
                [type.__str__(1) for type in ActionType if type.description is not None]
            ),
            friends=friends,
            tools=tools,
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            return "Your response is not in the correct schema.", False

        match = matches[0]

        return match[1].strip(), Decision(match[0]) == Decision.ACCEPT
