import re

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType

from .base import BaseOrganize

_TEMPLATE = """Your response should be in the following schema:
Type: action type
Name: action name
Instruction: action instruction
Extra: action extra

The action types you can use are:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Invite | Invite person who can do your work for you and are not your friends. | general person name | Personality | one of tools among {tool_names} that the person needs.
Talk |  Talk to your friends. | Friend's Name (should be one of {friend_names}) | Message | Attachment File List
Build | Build or rebuild a reusable tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py instruction extra` | Tool's Name (snake_case) | Tool's description that includes objective, instruction format, extra format, output format | Python Code for Building Tools (format: ```pythonprint("hello world")```)
Use | Use one of your tools. | Tool's Name (should be one of {tool_names}) | Tool Instruction for using tool | Extra for using tool

Your friends:{friends}
Your tools:{tools}

{prompt}
"""

_PATTERN = r"Type:\s*((?:\w| )+)\s+Name:\s*((?:\w| )+)\s+Instruction:\s*((?:(?!Extra:).)+)\s+Extra:\s*((?:(?!Type:).)*)\s*"


class Optimizer(BaseOrganize):
    template = _TEMPLATE
    pattern = _PATTERN

    def stringify(self, person: BasePerson, prompt: str) -> str:
        friends = "".join(
            [
                f"\n    {name}: {friend.instruction}"
                for name, friend in person.friends.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in person.tools.items()]
        )
        idea = self.planner_template.format(
            friends=friends,
            tools=tools,
            prompt=prompt,
        )
        return idea

    def parse(self, person: BasePerson, thought: str) -> list[Action]:
        matches = re.findall(self.action_pattern, thought, re.DOTALL)

        if len(matches) == 0:
            return [
                Action(
                    type=ActionType.Talk,
                    name=person.referee.name,
                    instruction=thought,
                    extra="",
                )
            ]

        return [
            Action(
                type=ActionType[match[0]],
                name=match[1],
                instruction=match[2],
                extra=match[3],
            )
            for match in matches
        ]
