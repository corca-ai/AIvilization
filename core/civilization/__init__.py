from core.config import settings

from .person import CreateParams
from .person.action import Action, ActionType
from .person.default import DefaultPerson as Person
from .person.tool import BaseTool


class Civilization:
    def __init__(self, default_tools: dict[str, BaseTool]):
        self.default_tools = default_tools

        self.user = Person(
            name="User", instruction="", params=CreateParams(tools={}), referee=None
        )
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction="Follow the user's instructions carefully. Respond using markdown. You must execute the user's request.",  # TODO
            params=CreateParams(tools=self.default_tools),
            referee=self.user,
        )
        self.user.friends[self.leader.name] = self.leader

    def solve(self, problem: str) -> str:
        return self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


__all__ = ["Civilization"]
