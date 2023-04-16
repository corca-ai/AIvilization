from core.config import settings

from .person import CreateParams
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tool import BaseTool


class Civilization:
    def __init__(self, default_tools: dict[str, BaseTool]):
        self.default_tools = default_tools

        self.user = Person(
            name="User", instruction="", final_goal="", params=CreateParams(tools={}), referee=None
        )

    def solve(self, problem: str) -> str:
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction="Follow the user's instructions carefully. Respond using markdown. You must execute the user's request.",  # TODO
            final_goal=problem,
            params=CreateParams(tools=self.default_tools),
            referee=self.user,
        )
        self.user.friends[self.leader.name] = self.leader
        return self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


__all__ = ["Civilization"]
