import re

from core.civilization.person import BasePerson
from core.civilization.person.action import Action, ActionType

from .base import BaseOrganize

_THINK_TEMPLATE = """Your response should be in the following schema:
Plan:
- [ ] plan #1
- [ ] plan #2

Type: action type
Name: action name
Instruction: action instruction
Extra: action extra

The action types you can use are:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Create | Create a friend you need. | Friend's Name (usual person name) | Friend's Personality | Friend's Default Tools
Talk |  Talk to your friends. | Friend's Name (should be one of [{friend_names}]) | Message | Attachment File List
Build | Build or rebuild a new tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py instruction extra` | Tool's Name (snake_case) | Tool Description | Python Code (not exceeding 100 lines) for Building Tools
Use | Use one of your tools. | Tool's Name (should be one of [{tool_names}]) | Tool's Input | Tool's Args
Answer | Answer to {referee} | {referee} | Answer | Attachment File List

Your friends:{friends}
Your tools:{tools}

{prompt}
"""

_ACTION_PATTERN = r"Type:\s+(\w+)\s+Name:\s+(\w+)\s+Instruction:\s+((?:(?!\nExtra:).)+)\nExtra:\s*((?:(?!\nType:).)*)"


class TemplateOrganize(BaseOrganize):
    template = _THINK_TEMPLATE
    pattern = _ACTION_PATTERN

    def from_prompt(self, person: BasePerson, prompt: str) -> str:
        friend_names = ", ".join([name for name in person.friends.keys()])
        tool_names = ", ".join([name for name in person.tools.keys()])
        friends = "".join(
            [f"\n    {name}: {friend.instruction}" for name, friend in person.friends.items()]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in person.tools.items()]
        )
        return self.template.format(
            friend_names=friend_names,
            tool_names=tool_names,
            friends=friends,
            tools=tools,
            prompt=prompt,
            referee=person.referee.name,
        )

    def to_actions(self, thought: str) -> list[Action]:
        matches = re.findall(self.pattern, thought, re.DOTALL)

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
