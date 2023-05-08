import re
from typing import Tuple

from core.civilization.person import BasePerson
from core.civilization.person.action import Action

from .base import BaseOrganize, Decision, WrongSchemaException

_TEMPLATE = """
## Background
The type of action you can take is:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Invite | Invite person who can do your work for you and are not your friends. | general person name | Personality | one of tools among {tool_names} that the person needs.
Talk |  Talk to your friends. | Friend's Name (should be one of {friend_names}) | Message | Attachment File List
Build | Build or rebuild a reusable tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py instruction extra` | Tool's Name (snake_case) | Tool's description that includes objective, instruction format, extra format, output format | Python Code for Building Tools (format: ```pythonprint("hello world")```)
Use | Use one of your tools. | Tool's Name (should be one of {tool_names}) | Tool Instruction for using tool | Extra for using tool

Your friends:{friends}
Your tools:{tools}

## Response
Your response is a review of the action and its results and you need to decide whether it is Accept or Reject.
Accept if the plan seems strange and write down your opinion. That opinion will be reflected and the plan will be redrawn.
==========your response schema==========
[Accept] or [Reject] your review of the action
==========  response example 1==========
[Reject] Actually, I think that the execution result is not good.
Let's make a new tool
==========  response example 2==========
[Accept] The execution result is perfect.
========================================

## Request
Review your execution result for executing "{plan}". Don't execute again, just say your opinion about action and result.
Your action is:
{action}
Your result of action is:
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
        tool_names = ", ".join([f"'{name}'" for name in person.tools.keys()])
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
            plan=plan,
            action=action,
            result=result,
            friend_names=friend_names,
            tool_names=tool_names,
            friends=friends,
            tools=tools,
        )

    def parse(self, person: BasePerson, thought: str) -> Tuple[str, bool]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

        if len(matches) != 1:
            return "Your response is not in the correct schema.", False

        match = matches[0]

        return match[1].strip(), Decision(match[0]) == Decision.ACCEPT
