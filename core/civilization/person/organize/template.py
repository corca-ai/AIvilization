import re

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType
from core.logging import ANSI, Color, logger

from .base import BaseOrganize

_THINK_TEMPLATE = """Your response should be in the following schema:
Plan: # Write your plan in markdown todo format.
- [ ] 

Type: action type
Name: action name
Instruction: action instruction
Extra: action extra

The action types you can use are:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Invite | Invite a friend who can do your work for you. | Friend's Name (usual person name) | Friend's Personality | Tools that your friend needs among the tools you have. ex. tool_name1, tool_name2
Talk |  Talk to your friends. | Friend's Name (should be one of [{friend_names}]) | Message | Attachment File List
Build | Build or rebuild a reusable tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py input extra_args` | Tool's Name (snake_case) | Tool's objective, input format, extra args format, output format | Python Code for Building Tools
Use | Use one of your tools. | Tool's Name (should be one of [{tool_names}]) | Tool Input for using tool | Extra Args

Your friends:{friends}
Your tools:{tools}

{prompt}
"""

_ACTION_PATTERN = r"Type:\s*(\w+)\s+Name:\s*(\w+)\s+Instruction:\s*((?:(?!Extra:).)+)\s+Extra:\s*((?:(?!Type:).)*)\s*"


class TemplateOrganize(BaseOrganize):
    template = _THINK_TEMPLATE
    action_pattern = _ACTION_PATTERN

    def from_prompt(self, person: BasePerson, prompt: str) -> str:
        friend_names = ", ".join([name for name in person.friends.keys()])
        tool_names = ", ".join([name for name in person.tools.keys()])
        friends = "".join(
            [
                f"\n    {name}: {friend.instruction}"
                for name, friend in person.friends.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in person.tools.items()]
        )
        idea = self.template.format(
            friend_names=friend_names,
            tool_names=tool_names,
            friends=friends,
            tools=tools,
            prompt=prompt,
            referee=person.referee.name,
        )

        logger.debug(ANSI(idea).to(Color.rgb(144, 144, 144)))

        return idea

    def to_actions(self, thought: str) -> list[Action]:
        logger.debug(ANSI(thought).to(Color.rgb(208, 208, 208)))

        matches = re.findall(self.action_pattern, thought, re.DOTALL)

        if len(matches) == 0:
            raise Exception("parse error")

        result = [
            Action(
                type=ActionType[match[0]],
                name=match[1],
                instruction=match[2],
                extra=match[3],
            )
            for match in matches
        ]

        return result
